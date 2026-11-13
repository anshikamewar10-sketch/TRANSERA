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
            "Inventory Receipt": ["Warehouse Database", "Inventory Database"],
            "Inventory Dispatch": ["Warehouse Database"],
            "Warehouse Transfer": ["Warehouse Database", "Inventory Database"],
            "Supplier Payment": ["Finance Database"],
            "Invoice Generation": ["Printer", "Invoice Generator"],
            "Customer Refund": ["Finance Database"],
            "Inventory Audit": ["Warehouse Database"],
            "Product Return": ["Inventory Database"],
        }

    # =====================================================
    # BUILD MAXIMUM MATRIX FROM ORACLE
    # =====================================================

    def build_maximum_matrix(self):

        cursor = self.connection.cursor()

        try:
            # Load all active processes
            cursor.execute("""
                SELECT PROCESS_ID
                FROM PROCESSES
                WHERE PROCESS_STATE IN (
                    'READY',
                    'RUNNING',
                    'AWAITING_RESOURCES',
                    'ALLOCATED',
                    'WAITING'
                )
                ORDER BY PROCESS_ID
            """)

            processes = [row[0] for row in cursor.fetchall()]

            maximum = {process_id: {} for process_id in processes}

            # Read maximum resource requirements
            cursor.execute("""
    SELECT
        PR.PROCESS_ID,
        PR.RESOURCE_ID,
        PR.MAX_UNITS
    FROM PROCESS_RESOURCE_REQUIREMENTS PR
    INNER JOIN PROCESSES P
        ON PR.PROCESS_ID = P.PROCESS_ID
    WHERE P.PROCESS_STATE IN (
        'READY',
        'RUNNING',
        'AWAITING_RESOURCES',
        'ALLOCATED',
        'WAITING'
    )
    ORDER BY PR.PROCESS_ID, PR.RESOURCE_ID
""")

            for process_id, resource_id, max_units in cursor.fetchall():

                maximum[process_id][resource_id] = int(max_units)

            # Prevent missing requirements from appearing safe
            missing = [
                process_id for process_id in processes if not maximum[process_id]
            ]

            if missing:
                raise ValueError(
                    "Missing resource requirements for: " + ", ".join(missing)
                )

            return maximum

        finally:
            cursor.close()
