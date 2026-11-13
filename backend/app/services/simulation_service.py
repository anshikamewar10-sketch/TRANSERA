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

        try:
            # ==========================================
            # COUNT PENDING OPERATIONS
            # ==========================================

            cursor.execute("""
                SELECT COUNT(*)
                FROM BUSINESS_OPERATIONS
                WHERE BUSINESS_STATUS = 'PENDING'
            """)

            total_pending = cursor.fetchone()[0]

            if total_pending == 0:
                return {"success": False, "message": "No Pending Operations Found."}

            # ==========================================
            # SIMULATION SIZE
            # ==========================================

            if simulate_all:
                limit = total_pending
            else:
                if number_of_operations <= 0:
                    return {
                        "success": False,
                        "message": "Number of operations must be positive.",
                    }

                limit = min(number_of_operations, total_pending)

            # ==========================================
            # LOAD PENDING OPERATIONS
            # ==========================================

            cursor.execute(
                """
                SELECT OPERATION_ID, PRIORITY
                FROM (
                    SELECT OPERATION_ID, PRIORITY
                    FROM BUSINESS_OPERATIONS
                    WHERE BUSINESS_STATUS = 'PENDING'
                    ORDER BY CREATED_AT, OPERATION_ID
                )
                WHERE ROWNUM <= :1
            """,
                (limit,),
            )

            operations = cursor.fetchall()

            # ==========================================
            # RESOURCE REQUIREMENT MAPPING
            # ==========================================

            resource_mapping = {
                "INVENTORY RECEIPT": {"RES001": 1, "RES002": 2, "RES005": 2},
                "SALES ORDER": {"RES002": 1, "RES005": 1, "RES006": 1},
                "INVOICE GENERATION": {"RES003": 1, "RES004": 1, "RES005": 1},
                "PURCHASE ORDER": {"RES001": 1, "RES002": 1, "RES005": 1},
                "STOCK TRANSFER": {"RES001": 1, "RES002": 1, "RES006": 1},
                "PAYROLL PROCESSING": {"RES005": 2, "RES006": 2, "RES007": 1},
                "INVENTORY AUDIT": {"RES001": 1, "RES005": 1},
                "REPORT GENERATION": {"RES005": 3, "RES006": 2},
            }

            # ==========================================
            # FIND NEXT PROCESS ID
            # ==========================================

            cursor.execute("""
            SELECT NVL(
            MAX(
            CASE
                WHEN REGEXP_LIKE(PROCESS_ID, '^PR[0-9]+$')
                THEN TO_NUMBER(SUBSTR(PROCESS_ID, 3))
                ELSE NULL
                 END
                 ),
                 0
                 )
                   FROM PROCESSES
            """)

            next_process = int(cursor.fetchone()[0])

            cursor.execute("""
                SELECT NVL(MAX(ARRIVAL_TIME), 0)
                FROM PROCESSES
            """)

            arrival_time = int(cursor.fetchone()[0]) + 1

            ready_queue = []

            # ==========================================
            # GENERATE PROCESSES
            # ==========================================

            for operation in operations:

                operation_id = operation[0]
                business_priority = operation[1]

                # Check whether process already exists
                cursor.execute(
                    """
                    SELECT COUNT(*)
                    FROM PROCESSES
                    WHERE OPERATION_ID = :1
                """,
                    (operation_id,),
                )

                if cursor.fetchone()[0] > 0:
                    continue

                # Convert business priority to numeric priority
                priority_text = (business_priority or "").strip().upper()

                if priority_text == "CRITICAL":
                    priority = 0
                elif priority_text == "HIGH":
                    priority = 1
                elif priority_text == "MEDIUM":
                    priority = 2
                else:
                    priority = 3

                # Get operation type
                cursor.execute(
                    """
                    SELECT OPERATION_TYPE
                    FROM BUSINESS_OPERATIONS
                    WHERE OPERATION_ID = :1
                """,
                    (operation_id,),
                )

                operation_row = cursor.fetchone()

                if operation_row is None:
                    raise ValueError(f"Operation {operation_id} not found.")

                operation_type = operation_row[0].strip().upper()

                if operation_type not in resource_mapping:
                    raise ValueError(f"No resource mapping for {operation_type}")

                # Generate unique process ID
                next_process += 1
                process_id = f"PR{next_process:03d}"

                # ==========================================
                # INSERT PROCESS
                # ==========================================

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
                    (process_id, operation_id, arrival_time, priority),
                )

                # ==========================================
                # INSERT RESOURCE REQUIREMENTS
                # ==========================================

                requirements = resource_mapping[operation_type]

                for resource_id, max_units in requirements.items():

                    cursor.execute(
                        """
                        INSERT INTO PROCESS_RESOURCE_REQUIREMENTS
                        (
                            PROCESS_ID,
                            RESOURCE_ID,
                            MAX_UNITS
                        )
                        VALUES (:1, :2, :3)
                    """,
                        (process_id, resource_id, max_units),
                    )

                # ==========================================
                # UPDATE BUSINESS OPERATION
                # ==========================================

                cursor.execute(
                    """
                    UPDATE BUSINESS_OPERATIONS
                    SET BUSINESS_STATUS = 'PROCESSING'
                    WHERE OPERATION_ID = :1
                      AND BUSINESS_STATUS = 'PENDING'
                """,
                    (operation_id,),
                )

                if cursor.rowcount != 1:
                    raise RuntimeError(f"Could not update operation {operation_id}.")

                print(
                    f"{operation_id} -> {process_id} "
                    "created and moved to READY queue."
                )

                ready_queue.append(
                    {
                        "process_id": process_id,
                        "operation_id": operation_id,
                        "arrival_time": arrival_time,
                        "priority": priority,
                        "state": "READY",
                    }
                )

                arrival_time += 1

            # ==========================================
            # COMMIT ALL CHANGES TOGETHER
            # ==========================================

            self.connection.commit()

            return {
                "success": True,
                "summary": {
                    "pending_operations": total_pending,
                    "processes_created": len(ready_queue),
                    "ready_queue_size": len(ready_queue),
                },
                "ready_queue": ready_queue,
                "message": "Simulation Started Successfully.",
            }

        except Exception:
            self.connection.rollback()
            raise

        finally:
            cursor.close()
