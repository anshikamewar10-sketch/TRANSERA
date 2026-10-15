"""
---------------------------------------------------------
Resource Service
---------------------------------------------------------
Purpose:
Controls Resource Allocation and Waiting Queue.
---------------------------------------------------------
"""

from app.database.connection import get_connection

from app.services.resource.allocator import ResourceAllocator
from app.services.resource.waiting_queue import WaitingQueue


class ResourceService:

    def __init__(self):

        self.connection = get_connection()

        self.allocator = ResourceAllocator()
        self.waiting = WaitingQueue()

    # =====================================================
    # RESOURCE CENTER
    # =====================================================

    def manage_resources(self):

        cursor = self.connection.cursor()

        try:
            # Load all processes awaiting resources
            cursor.execute("""
                SELECT PROCESS_ID, OPERATION_ID
                FROM PROCESSES
                WHERE PROCESS_STATE = 'AWAITING_RESOURCES'
                ORDER BY ARRIVAL_TIME, PROCESS_ID
            """)

            processes = cursor.fetchall()

        finally:
            cursor.close()

        if not processes:
            return {"success": False, "message": "No processes awaiting resources."}

        results = []

        for process_id, operation_id in processes:

            cursor = self.allocator.connection.cursor()

            try:
                # Find operation type
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
                    raise ValueError(f"Operation not found for {process_id}")

                operation_type = operation_row[0]

                required_resources = self.allocator.get_required_resources(
                    operation_type
                )

                # Find resources already allocated
                cursor.execute(
                    """
                    SELECT R.RESOURCE_NAME
                    FROM RESOURCE_ALLOCATIONS RA
                    JOIN RESOURCES R
                      ON RA.RESOURCE_ID = R.RESOURCE_ID
                    WHERE RA.PROCESS_ID = :1
                      AND RA.ALLOCATION_STATUS = 'ALLOCATED'
                """,
                    (process_id,),
                )

                existing = {row[0] for row in cursor.fetchall()}

            finally:
                cursor.close()

            missing_resources = [
                name for name in required_resources if name not in existing
            ]

            newly_allocated = []
            waiting_resources = []

            # Allocate only resources not already held
            if missing_resources:

                allocation = self.allocator.allocate_resources(process_id)

                if not allocation["success"]:
                    raise RuntimeError(
                        allocation.get("message", "Resource allocation failed.")
                    )

                newly_allocated = allocation.get("allocated_resources", [])

                waiting_resources = allocation.get("waiting_resources", [])
                # Verify that all required resources are held
                held_resources = set(existing) | set(newly_allocated)

                waiting_resources = [
                    name for name in required_resources
                       if name not in held_resources
                     ]
            if waiting_resources:

                self.waiting.move_to_waiting(process_id)
                status = "WAITING"

            else:

                status = "ALLOCATED"

                # Keep allocated processes out of the
                # AWAITING_RESOURCES selection on retries.
                cursor = self.connection.cursor()

                try:
                    cursor.execute(
                        """
                        UPDATE PROCESSES
                        SET PROCESS_STATE = 'ALLOCATED'
                        WHERE PROCESS_ID = :1
                          AND PROCESS_STATE =
                              'AWAITING_RESOURCES'
                    """,
                        (process_id,),
                    )

                    self.connection.commit()

                except Exception:
                    self.connection.rollback()
                    raise

                finally:
                    cursor.close()

            results.append(
                {
                    "process_id": process_id,
                    "status": status,
                    "allocated_resources": sorted(existing) + newly_allocated,
                    "waiting_resources": waiting_resources,
                }
            )

        waiting_queue = self.waiting.get_waiting_queue()

        return {
            "success": True,
            "total_processed": len(results),
            "results": results,
            "waiting_queue": waiting_queue,
            "message": "Resource Allocation Processing Completed.",
        }

        # =====================================================

    # RESOURCE HISTORY
    # =====================================================

    def get_resource_history(self):

        cursor = self.allocator.connection.cursor()

        cursor.execute("""
            SELECT
                RA.PROCESS_ID,
                R.RESOURCE_NAME,
                RA.ALLOCATION_STATUS,
                RA.ALLOCATION_TIME
            FROM RESOURCE_ALLOCATIONS RA
            JOIN RESOURCES R
            ON RA.RESOURCE_ID = R.RESOURCE_ID
            ORDER BY RA.ALLOCATION_TIME DESC
            """)

        rows = cursor.fetchall()

        cursor.close()

        history = []

        for row in rows:

            history.append(
                {
                    "process_id": row[0],
                    "resource_name": row[1],
                    "allocation_status": row[2],
                    "allocation_time": row[3].strftime("%Y-%m-%d %H:%M:%S"),
                }
            )

        return {"success": True, "history": history}
