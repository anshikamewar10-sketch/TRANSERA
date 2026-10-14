
"""
---------------------------------------------------------
Scheduler Service
---------------------------------------------------------
Purpose:
Loads READY processes, generates scheduling order,
starts processes and completes CPU bursts.
---------------------------------------------------------
"""

from app.database.connection import get_connection

from app.services.scheduler.fcfs import FCFS
from app.services.scheduler.sjf import SJF
from app.services.scheduler.priority import PriorityScheduling
from app.services.scheduler.round_robin import RoundRobin


class SchedulerService:

    def __init__(self):
        self.connection = get_connection()

    # =====================================================
    # LOAD READY QUEUE
    # =====================================================

    def load_ready_queue(self):

        cursor = self.connection.cursor()

        try:
            cursor.execute("""
                SELECT
                    PROCESS_ID,
                    OPERATION_ID,
                    ARRIVAL_TIME,
                    BURST_TIME,
                    PRIORITY
                FROM PROCESSES
                WHERE PROCESS_STATE = 'READY'
                ORDER BY ARRIVAL_TIME, PROCESS_ID
            """)

            rows = cursor.fetchall()

            ready_queue = []

            for row in rows:
                ready_queue.append({
                    "process_id": row[0],
                    "operation_id": row[1],
                    "arrival_time": row[2],
                    "burst_time": row[3],
                    "priority": row[4]
                })

            return ready_queue

        finally:
            cursor.close()

    # =====================================================
    # EXECUTE SCHEDULER
    # =====================================================

    def execute_scheduler(self, algorithm):

        ready_queue = self.load_ready_queue()

        if algorithm.upper() == "FCFS":
            scheduler = FCFS()

        elif algorithm.upper() == "SJF":
            scheduler = SJF()

        elif algorithm.upper() == "PRIORITY":
            scheduler = PriorityScheduling()

        elif algorithm.upper() == "ROUND_ROBIN":
            scheduler = RoundRobin()

        else:
            return {
                "success": False,
                "message": "Invalid Scheduling Algorithm."
            }

        return scheduler.run(ready_queue)

    # =====================================================
    # START RUNNING PROCESS
    # =====================================================

    def start_running_process(self, process_id):

        cursor = self.connection.cursor()

        try:
            cursor.execute("""
                LOCK TABLE PROCESSES IN EXCLUSIVE MODE
            """)

            cursor.execute("""
                SELECT PROCESS_STATE
                FROM PROCESSES
                WHERE PROCESS_ID = :1
            """, (process_id,))

            row = cursor.fetchone()

            if row is None or row[0] != "READY":
                self.connection.rollback()
                return {
                    "success": False,
                    "message": "Process not found or not READY."
                }

            cursor.execute("""
                SELECT COUNT(*)
                FROM PROCESSES
                WHERE PROCESS_STATE = 'RUNNING'
            """)

            if cursor.fetchone()[0] > 0:
                self.connection.rollback()
                return {
                    "success": False,
                    "message": "Another process is already RUNNING."
                }

            cursor.execute("""
                UPDATE PROCESSES
                SET PROCESS_STATE = 'RUNNING'
                WHERE PROCESS_ID = :1
            """, (process_id,))

            self.connection.commit()

            return {
                "success": True,
                "process_id": process_id,
                "process_state": "RUNNING",
                "message": f"{process_id} is now RUNNING."
            }

        except Exception:
            self.connection.rollback()
            raise

        finally:
            cursor.close()

    # =====================================================
    # COMPLETE CPU BURST
    # =====================================================

    def complete_cpu_burst(self, process_id):

        cursor = self.connection.cursor()

        try:
            cursor.execute("""
                UPDATE PROCESSES
                SET PROCESS_STATE = 'AWAITING_RESOURCES'
                WHERE PROCESS_ID = :1
                AND PROCESS_STATE = 'RUNNING'
            """, (process_id,))

            if cursor.rowcount == 0:
                self.connection.rollback()

                return {
                    "success": False,
                    "message": "Process is not RUNNING."
                }

            self.connection.commit()

            return {
                "success": True,
                "process_id": process_id,
                "process_state": "AWAITING_RESOURCES",
                "message": "CPU Burst Completed. Awaiting Resources."
            }

        except Exception:
            self.connection.rollback()
            raise

        finally:
            cursor.close()
