"""
---------------------------------------------------------
Deadlock Common Functions
---------------------------------------------------------
Purpose:
Reads process, resource and allocation
information from Oracle Database.
---------------------------------------------------------
"""

from app.database.connection import get_connection


class DeadlockCommon:

    def __init__(self):

        self.connection = get_connection()

    # ==========================================
    # PROCESS LIST
    # ==========================================

    def get_processes(self):

        cursor = self.connection.cursor()

        cursor.execute("""
            SELECT PROCESS_ID
            FROM PROCESSES
            ORDER BY PROCESS_ID
        """)

        rows = cursor.fetchall()

        cursor.close()

        return [row[0] for row in rows]

    # ==========================================
    # RESOURCE LIST
    # ==========================================

    def get_resources(self):

        cursor = self.connection.cursor()

        cursor.execute("""
            SELECT
                RESOURCE_ID,
                AVAILABLE_UNITS
            FROM RESOURCES
            ORDER BY RESOURCE_ID
        """)

        rows = cursor.fetchall()

        cursor.close()

        return rows

    # ==========================================
    # CURRENT ALLOCATION
    # ==========================================

    def get_allocations(self):

        cursor = self.connection.cursor()

        cursor.execute("""
            SELECT
                PROCESS_ID,
                RESOURCE_ID
            FROM RESOURCE_ALLOCATIONS
            WHERE ALLOCATION_STATUS='ALLOCATED'
        """)

        rows = cursor.fetchall()

        cursor.close()

        return rows

    # ==========================================
    # MAXIMUM NEED
    # ==========================================

    def maximum_need(self):

        return {

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
        
        # ==========================================
    # BUILD MAXIMUM MATRIX
    # ==========================================

    def build_maximum_matrix(self):

        cursor = self.connection.cursor()

        cursor.execute("""
            SELECT
                P.PROCESS_ID,
                B.OPERATION_TYPE
            FROM PROCESSES P
            JOIN BUSINESS_OPERATIONS B
            ON P.OPERATION_ID = B.OPERATION_ID
        """)

        processes = cursor.fetchall()

        cursor.execute("""
            SELECT
                RESOURCE_ID,
                RESOURCE_NAME
            FROM RESOURCES
        """)

        resources = cursor.fetchall()

        cursor.close()

        resource_map = {}

        for resource_id, resource_name in resources:

            resource_map[resource_name] = resource_id

        operation_mapping = self.maximum_need()

        maximum = {}

        for process_id, operation_type in processes:

            maximum[process_id] = {}

            required = operation_mapping.get(
                operation_type,
                []
            )

            for resource_name in required:

                resource_id = resource_map.get(
                    resource_name
                )

                if resource_id:

                    maximum[process_id][resource_id] = 1

        return maximum