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
    
        # ==============================================
    # RELEASE RESOURCES
    # ==============================================

    def release_resources(self, process_id):

        cursor = self.connection.cursor()

        cursor.execute(
            """
            SELECT RESOURCE_ID
            FROM RESOURCE_ALLOCATIONS
            WHERE PROCESS_ID = :1
            AND ALLOCATION_STATUS = 'ALLOCATED'
            """,
            (
                process_id,
            )
        )

        resources = cursor.fetchall()

        for resource in resources:

            resource_id = resource[0]

            cursor.execute(
                """
                UPDATE RESOURCES
                SET AVAILABLE_UNITS = AVAILABLE_UNITS + 1
                WHERE RESOURCE_ID = :1
                """,
                (
                    resource_id,
                )
            )
            cursor.execute(
                """
                SELECT RESOURCE_NAME
                FROM RESOURCES
                WHERE RESOURCE_ID = :1
                """,
                (
                    resource_id,
                )
            )

            resource_name = cursor.fetchone()[0]

            self.write_log(
                process_id,
                "RESOURCE_RELEASED",
                f"{resource_name} Released"
            )

        cursor.execute(
            """
            UPDATE RESOURCE_ALLOCATIONS
            SET ALLOCATION_STATUS = 'RELEASED'
            WHERE PROCESS_ID = :1
            """,
            (
                process_id,
            )
        )

        self.connection.commit()

        cursor.close()