
"""
TRANSERA - Scheduler Service

Controls Oracle CPU process states for:
FCFS, SJF, Priority and Round Robin.

Resource allocation and deadlock handling remain separate.
"""

from app.database.connection import get_connection

from app.services.scheduler.fcfs import FCFS
from app.services.scheduler.sjf import SJF
from app.services.scheduler.priority import PriorityScheduling
from app.services.scheduler.round_robin import RoundRobin


class SchedulerService:

    ALGORITHMS = {
        "FCFS": FCFS,
        "SJF": SJF,
        "PRIORITY": PriorityScheduling,
        "ROUND_ROBIN": RoundRobin
    }

    def load_ready_queue(self):

        connection = get_connection()
        cursor = connection.cursor()

        try:
            cursor.execute("""
                SELECT
                    PROCESS_ID,
                    OPERATION_ID,
                    ARRIVAL_TIME,
                    BURST_TIME,
                    PRIORITY,
                    REMAINING_BURST_TIME
                FROM PROCESSES
                WHERE PROCESS_STATE = 'READY'
                ORDER BY ARRIVAL_TIME, PROCESS_ID
            """)

            return [
                {
                    "process_id": row[0],
                    "operation_id": row[1],
                    "arrival_time": float(row[2]),
                    "burst_time": float(row[3]),
                    "priority": int(row[4]),
                    "remaining_burst_time": (
                        float(row[5])
                        if row[5] is not None
                        else None
                    )
                }
                for row in cursor.fetchall()
            ]

        finally:
            cursor.close()
            connection.close()

    def execute_scheduler(self, algorithm):

        algorithm = algorithm.upper()

        if algorithm not in self.ALGORITHMS:
            return {
                "success": False,
                "message": "Invalid Scheduling Algorithm."
            }

        ready_queue = self.load_ready_queue()

        if not ready_queue:
            return {
                "success": False,
                "message": "No READY Processes Found."
            }

        if any(
            p["burst_time"] <= 0
            or p["remaining_burst_time"] is not None
            and p["remaining_burst_time"] <= 0
            for p in ready_queue
        ):
            return {
                "success": False,
                "message": "Invalid CPU burst time detected."
            }

        if any(
            p["remaining_burst_time"] is not None
            and p["remaining_burst_time"] < p["burst_time"]
            for p in ready_queue
        ):
            return {
                "success": False,
                "message": (
                    "An unfinished CPU burst already exists. "
                    "Resume the same scheduling run."
                )
            }

        scheduler = self.ALGORITHMS[algorithm]()

        return scheduler.run(ready_queue)

    def start_running_process(
        self, process_id, algorithm="FCFS"
    ):

        algorithm = algorithm.upper()

        if algorithm not in self.ALGORITHMS:
            return {
                "success": False,
                "message": "Invalid scheduling algorithm."
            }

        connection = get_connection()
        cursor = connection.cursor()

        try:
            cursor.execute("""
                LOCK TABLE PROCESSES IN EXCLUSIVE MODE
            """)

            cursor.execute("""
                SELECT
                    PROCESS_STATE,
                    BURST_TIME,
                    REMAINING_BURST_TIME,
                    ALGORITHM_USED
                FROM PROCESSES
                WHERE PROCESS_ID = :1
            """, (process_id,))

            row = cursor.fetchone()

            if not row or row[0] != "READY":
                connection.rollback()
                return {
                    "success": False,
                    "message": "Process not found or not READY."
                }

            state, burst, remaining, previous_algorithm = row

            if previous_algorithm not in (None, algorithm):
                connection.rollback()
                return {
                    "success": False,
                    "message": (
                        "Process already belongs to another "
                        "scheduling algorithm."
                    )
                }

            cursor.execute("""
                SELECT COUNT(*)
                FROM PROCESSES
                WHERE PROCESS_STATE = 'RUNNING'
            """)

            if cursor.fetchone()[0] > 0:
                connection.rollback()
                return {
                    "success": False,
                    "message": "Another process is already RUNNING."
                }

            cursor.execute("""
                UPDATE PROCESSES
                SET PROCESS_STATE = 'RUNNING',
                    ALGORITHM_USED = :1,
                    REMAINING_BURST_TIME =
                        NVL(REMAINING_BURST_TIME, BURST_TIME)
                WHERE PROCESS_ID = :2
                  AND PROCESS_STATE = 'READY'
            """, (algorithm, process_id))

            if cursor.rowcount != 1:
                raise RuntimeError("Process state update failed.")

            connection.commit()

            return {
                "success": True,
                "process_id": process_id,
                "process_state": "RUNNING",
                "algorithm": algorithm,
                "remaining_burst_time": (
                    float(remaining)
                    if remaining is not None
                    else float(burst)
                ),
                "message": f"{process_id} is now RUNNING."
            }

        except Exception:
            connection.rollback()
            raise

        finally:
            cursor.close()
            connection.close()

    def complete_cpu_burst(self, process_id):

        connection = get_connection()
        cursor = connection.cursor()

        try:
            cursor.execute("""
                SELECT
                    PROCESS_STATE,
                    ALGORITHM_USED
                FROM PROCESSES
                WHERE PROCESS_ID = :1
                FOR UPDATE
            """, (process_id,))

            row = cursor.fetchone()

            if not row or row[0] != "RUNNING":
                connection.rollback()
                return {
                    "success": False,
                    "message": "Process is not RUNNING."
                }

            if row[1] == "ROUND_ROBIN":
                connection.rollback()
                return {
                    "success": False,
                    "message": (
                        "Use the Round Robin quantum endpoint."
                    )
                }

            cursor.execute("""
             UPDATE PROCESSES
              SET PROCESS_STATE = 'AWAITING_RESOURCES',
              REMAINING_BURST_TIME = 0
                   WHERE PROCESS_ID = :1
               AND PROCESS_STATE = 'RUNNING'
              """, (process_id,))

            if cursor.rowcount != 1:
                raise RuntimeError("CPU completion failed.")

            connection.commit()

            return {
                "success": True,
                "process_id": process_id,
                "process_state": "AWAITING_RESOURCES",
                "remaining_burst_time": 0,
                "message": (
                    "CPU Burst Completed. Awaiting Resources."
                )
            }

        except Exception:
            connection.rollback()
            raise

        finally:
            cursor.close()
            connection.close()

    def complete_quantum(self, process_id, duration):

        connection = get_connection()
        cursor = connection.cursor()

        try:
            cursor.execute("""
                SELECT
                    PROCESS_STATE,
                    BURST_TIME,
                    REMAINING_BURST_TIME,
                    ALGORITHM_USED
                FROM PROCESSES
                WHERE PROCESS_ID = :1
                FOR UPDATE
            """, (process_id,))

            row = cursor.fetchone()

            if not row or row[0] != "RUNNING":
                connection.rollback()
                return {
                    "success": False,
                    "message": "Process is not RUNNING."
                }

            state, burst, remaining, algorithm = row

            if algorithm != "ROUND_ROBIN":
                connection.rollback()
                return {
                    "success": False,
                    "message": "Process is not using Round Robin."
                }

            if remaining is None:
                remaining = burst

            remaining = float(remaining)
            duration = float(duration)

            if (
                duration <= 0
                or duration > 2
                or duration > remaining
            ):
                connection.rollback()
                return {
                    "success": False,
                    "message": "Invalid CPU quantum duration."
                }

            new_remaining = max(0, remaining - duration)

            if new_remaining == 0:
                new_state = "AWAITING_RESOURCES"
            else:
                new_state = "READY"

            cursor.execute("""
                   UPDATE PROCESSES
                 SET PROCESS_STATE = :1,
                 REMAINING_BURST_TIME = :2
                WHERE PROCESS_ID = :3
                   AND PROCESS_STATE = 'RUNNING'
                 """, (
            new_state,
            new_remaining,
            process_id
               ))

            if cursor.rowcount != 1:
                raise RuntimeError("Quantum update failed.")

            connection.commit()

            return {
                "success": True,
                "process_id": process_id,
                "process_state": new_state,
                "remaining_burst_time": new_remaining,
                "completed": new_remaining == 0,
                "message": (
                    "CPU burst completed. Awaiting Resources."
                    if new_remaining == 0
                    else "Quantum expired. Process returned to READY."
                )
            }

        except Exception:
            connection.rollback()
            raise

        finally:
            cursor.close()
            connection.close()
