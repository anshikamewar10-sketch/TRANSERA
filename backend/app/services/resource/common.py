"""
---------------------------------------------------------
Resource Common Functions
---------------------------------------------------------
Purpose:
Shared database functions used by Resource Center.
---------------------------------------------------------
"""

from app.database.connection import get_connection


class ResourceCommon:

    def __init__(self):

        self.connection = get_connection()

    # =====================================================
    # GET RUNNING PROCESS
    # =====================================================

    def get_running_process(self):

        cursor = self.connection.cursor()

        cursor.execute("""
            SELECT
                PROCESS_ID,
                OPERATION_ID
            FROM PROCESSES
            WHERE PROCESS_STATE='RUNNING'
        """)

        process = cursor.fetchone()

        cursor.close()

        return process

    # =====================================================
    # GET REQUIRED RESOURCES
    # =====================================================

    def get_required_resources(self, operation_type):

        RESOURCE_MAPPING = {

            "Inventory Receipt":
            [
                "Warehouse Database",
                "Inventory Database"
            ],

            "Inventory Dispatch":
            [
                "Warehouse Database"
            ],

            "Warehouse Transfer":
            [
                "Warehouse Database",
                "Inventory Database"
            ],

            "Supplier Payment":
            [
                "Finance Database"
            ],

            "Invoice Generation":
            [
                "Printer",
                "Invoice Generator"
            ],

            "Customer Refund":
            [
                "Finance Database"
            ],

            "Inventory Audit":
            [
                "Warehouse Database"
            ],

            "Product Return":
            [
                "Inventory Database"
            ]

        }

        return RESOURCE_MAPPING.get(
            operation_type,
            []
        )
    
    
    
    
    # =====================================================
    # GET PROCESS RESOURCE REQUIREMENTS
    # =====================================================

    def get_process_requirements(self, process_id):

        cursor = self.connection.cursor()

        try:
            cursor.execute("""
                SELECT
                    R.RESOURCE_ID,
                    R.RESOURCE_NAME,
                    PR.MAX_UNITS
                FROM PROCESS_RESOURCE_REQUIREMENTS PR
                JOIN RESOURCES R
                    ON PR.RESOURCE_ID = R.RESOURCE_ID
                WHERE PR.PROCESS_ID = :1
                ORDER BY R.RESOURCE_ID
            """, (process_id,))

            rows = cursor.fetchall()

            requirements = {}

            for resource_id, resource_name, max_units in rows:

                requirements[resource_id] = {
                    "resource_name": resource_name,
                    "max_units": int(max_units)
                }

            return requirements

        finally:
            cursor.close()
    
    
    
    # =====================================================
    # GET RESOURCE ID
    # =====================================================

    def get_resource_id(self,
                        resource_name):

        cursor = self.connection.cursor()

        cursor.execute(
            """
            SELECT RESOURCE_ID
            FROM RESOURCES
            WHERE RESOURCE_NAME=:1
            """,
            (
                resource_name,
            )
        )

        row = cursor.fetchone()

        cursor.close()

        if row:

            return row[0]

        return None
    
       

   
    # ==========================================
    # RELEASE RESOURCE INSTANCES
    # ==========================================

    def release_resources(self, process_id):

        cursor = self.connection.cursor()

        try:
            cursor.execute("""
                SELECT
                    ALLOCATION_ID,
                    RESOURCE_ID,
                    ALLOCATED_UNITS
                FROM RESOURCE_ALLOCATIONS
                WHERE PROCESS_ID = :1
                  AND ALLOCATION_STATUS = 'ALLOCATED'
                FOR UPDATE
            """, (process_id,))

            allocations = cursor.fetchall()

            if not allocations:
                return {
                    "success": False,
                    "process_id": process_id,
                    "message": "No active allocations found."
                }

            released = []

            for allocation_id, resource_id, units in allocations:

                units = int(units)

                cursor.execute("""
                    UPDATE RESOURCES
                    SET AVAILABLE_UNITS = AVAILABLE_UNITS + :1
                    WHERE RESOURCE_ID = :2
                      AND AVAILABLE_UNITS + :1 <= TOTAL_UNITS
                """, (units, resource_id))

                if cursor.rowcount != 1:
                    raise RuntimeError(
                        "Resource capacity validation failed."
                    )

                cursor.execute("""
                    UPDATE RESOURCE_ALLOCATIONS
                    SET ALLOCATION_STATUS = 'RELEASED'
                    WHERE ALLOCATION_ID = :1
                      AND ALLOCATION_STATUS = 'ALLOCATED'
                """, (allocation_id,))

                if cursor.rowcount != 1:
                    raise RuntimeError(
                        "Allocation release update failed."
                    )

                released.append({
                    "resource_id": resource_id,
                    "units_released": units
                })

            return {
                "success": True,
                "process_id": process_id,
                "released_resources": released,
                "message": "Resources released successfully."
            }

        except Exception:
            self.connection.rollback()
            raise

        finally:
            cursor.close()
