"""
---------------------------------------------------------
Resource Allocator
---------------------------------------------------------
Purpose:
Allocates required resources to the currently
running process.
---------------------------------------------------------
"""

from app.services.resource.common import ResourceCommon


class ResourceAllocator(ResourceCommon):

    def allocate_resources(self, process_id):

        cursor = self.connection.cursor()

        # -----------------------------------------
        # GET OPERATION ID
        # -----------------------------------------

        cursor.execute(
            """
            SELECT OPERATION_ID
            FROM PROCESSES
            WHERE PROCESS_ID = :1
            """,
            (process_id,),
        )

        row = cursor.fetchone()

        if row is None:

            cursor.close()

            return {"success": False, "message": "Running Process Not Found."}

        operation_id = row[0]

        # -----------------------------------------
        # GET OPERATION TYPE
        # -----------------------------------------

        cursor.execute(
            """
            SELECT OPERATION_TYPE
            FROM BUSINESS_OPERATIONS
            WHERE OPERATION_ID = :1
            """,
            (operation_id,),
        )

        operation_type = cursor.fetchone()[0]

        # -----------------------------------------
        # GET REQUIRED RESOURCES
        # -----------------------------------------

        required_resources = self.get_required_resources(operation_type)

        allocated = []
        waiting = []

        # -----------------------------------------
        # ALLOCATE RESOURCES
        # -----------------------------------------

        for resource_name in required_resources:

            # Check whether this process already holds the resource
            cursor.execute(
                """
                SELECT COUNT(*)
                FROM RESOURCE_ALLOCATIONS RA
                JOIN RESOURCES R
                    ON RA.RESOURCE_ID = R.RESOURCE_ID
                WHERE RA.PROCESS_ID = :1
                  AND R.RESOURCE_NAME = :2
                  AND RA.ALLOCATION_STATUS = 'ALLOCATED'
            """,
                (process_id, resource_name),
            )

            already_allocated = cursor.fetchone()[0]

            if already_allocated > 0:
                continue

            resource_id = self.get_resource_id(resource_name)

            # Atomically reserve one available unit
            cursor.execute(
                """
                UPDATE RESOURCES
                SET AVAILABLE_UNITS = AVAILABLE_UNITS - 1
                WHERE RESOURCE_ID = :1
                  AND AVAILABLE_UNITS > 0
            """,
                (resource_id,),
            )

            if cursor.rowcount > 0:

                cursor.execute("""
                    SELECT NVL(
                        MAX(TO_NUMBER(SUBSTR(ALLOCATION_ID, 3))),
                        0
                    ) + 1
                    FROM RESOURCE_ALLOCATIONS
                """)

                next_id = cursor.fetchone()[0]
                allocation_id = f"RA{next_id:03d}"

                cursor.execute(
                    """
                    INSERT INTO RESOURCE_ALLOCATIONS
                    (
                        ALLOCATION_ID,
                        PROCESS_ID,
                        RESOURCE_ID,
                        ALLOCATED_UNITS,
                        ALLOCATION_STATUS,
                        ALLOCATION_TIME
                    )
                    VALUES
                    (
                        :1, :2, :3, 1,
                        'ALLOCATED',
                        CURRENT_TIMESTAMP
                    )
                """,
                    (allocation_id, process_id, resource_id),
                )

                allocated.append(resource_name)

            else:
                waiting.append(resource_name)

        self.connection.commit()

        cursor.close()

        return {
            "success": True,
            "process_id": process_id,
            "allocated_resources": allocated,
            "waiting_resources": waiting,
        }
