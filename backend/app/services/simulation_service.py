"""
---------------------------------------------------------
Simulation Service
---------------------------------------------------------
Purpose:
Converts Pending Business Operations into
Operating System Processes.
---------------------------------------------------------
"""

from app.database.connection import get_connection


class SimulationService:

    def __init__(self):
        self.connection = get_connection()

    def start_simulation(self, simulate_all: bool, number_of_operations: int):

        cursor = self.connection.cursor()

        # ==========================================
        # COUNT PENDING OPERATIONS
        # ==========================================

        cursor.execute("""
            SELECT COUNT(*)
            FROM BUSINESS_OPERATIONS
            WHERE BUSINESS_STATUS='PENDING'
        """)

        total_pending = cursor.fetchone()[0]

        if total_pending == 0:

            cursor.close()

            return {
                "success": False,
                "message": "No Pending Operations Found."
            }

        # ==========================================
        # SIMULATION SIZE
        # ==========================================

        if simulate_all:
            limit = total_pending
        else:
            limit = min(number_of_operations, total_pending)

        # ==========================================
        # LOAD PENDING OPERATIONS
        # ==========================================

        cursor.execute(f"""
            SELECT
                OPERATION_ID,
                PRIORITY
            FROM
            (
                SELECT
                    OPERATION_ID,
                    PRIORITY
                FROM BUSINESS_OPERATIONS
                WHERE BUSINESS_STATUS='PENDING'
                ORDER BY CREATED_AT
            )
            WHERE ROWNUM <= {limit}
        """)

        operations = cursor.fetchall()

        arrival_time = 1

        ready_queue = []

        # ==========================================
        # GENERATE PROCESSES
        # ==========================================

        for operation in operations:

            operation_id = operation[0]

            cursor.execute("""
                SELECT COUNT(*)
                FROM PROCESSES
                WHERE OPERATION_ID=:1
            """,
            (
                operation_id,
            ))

            process_exists = cursor.fetchone()[0]

            if process_exists > 0:
                continue

            business_priority = operation[1]

            if business_priority == "HIGH":
                priority = 1

            elif business_priority == "MEDIUM":
                priority = 2

            else:
                priority = 3

            cursor.execute("""
                SELECT NVL(MAX(TO_NUMBER(SUBSTR(PROCESS_ID,3))),0)+1
                FROM PROCESSES
            """)

            next_process = cursor.fetchone()[0]

            process_id = f"PR{next_process:03d}"

            cursor.execute(
                """
                INSERT INTO PROCESSES
                (
                    PROCESS_ID,
                    OPERATION_ID,
                    PROCESS_STATE,
                    ARRIVAL_TIME,
                    BURST_TIME,
                    PRIORITY,
                    ALGORITHM_USED,
                    COMPLETION_TIME
                )
                VALUES
                (
                    :1,
                    :2,
                    'READY',
                    :3,
                    5,
                    :4,
                    NULL,
                    NULL
                )
                """,
                (
                    process_id,
                    operation_id,
                    arrival_time,
                    priority
                )
            )

            cursor.execute(
                """
                UPDATE BUSINESS_OPERATIONS
                SET BUSINESS_STATUS='PROCESSING'
                WHERE OPERATION_ID=:1
                """,
                (
                    operation_id,
                )
            )
            print(f"{operation_id} -> {process_id} created and moved to READY queue.")

            ready_queue.append(
                {
                    "process_id": process_id,
                    "operation_id": operation_id,
                    "arrival_time": arrival_time,
                    "priority": priority,
                    "state": "READY"
                }
            )

            arrival_time += 1

        self.connection.commit()

        cursor.close()

        return {
            "success": True,
            "summary": {
                "pending_operations": total_pending,
                "processes_created": len(ready_queue),
                "ready_queue_size": len(ready_queue)
            },
            "ready_queue": ready_queue,
            "message": "Simulation Started Successfully."
        }