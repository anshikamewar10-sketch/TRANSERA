"""
---------------------------------------------------------
Deadlock Service
---------------------------------------------------------
Purpose:
Reads Oracle data, runs Banker's Algorithm
and resolves deadlock if required.
---------------------------------------------------------
"""

from app.services.deadlock.common import DeadlockCommon
from app.services.deadlock.bankers import BankersAlgorithm
from app.services.deadlock.resolver import DeadlockResolver


class DeadlockService(DeadlockCommon):

    def __init__(self):

        super().__init__()

        self.banker = BankersAlgorithm()
        self.resolver = DeadlockResolver()

    # =====================================================
    # CHECK DEADLOCK
    # =====================================================

    def check_deadlock(self):

        cursor = self.connection.cursor()

        # -----------------------------------------
        # AVAILABLE RESOURCES
        # -----------------------------------------

        cursor.execute("""
            SELECT RESOURCE_ID,
                   AVAILABLE_UNITS
            FROM RESOURCES
        """)

        available = {}

        for row in cursor.fetchall():

            available[row[0]] = row[1]

        # -----------------------------------------
        # CURRENT ALLOCATION
        # -----------------------------------------

        cursor.execute("""
            SELECT
                PROCESS_ID,
                RESOURCE_ID,
                ALLOCATED_UNITS
            FROM RESOURCE_ALLOCATIONS
            WHERE ALLOCATION_STATUS='ALLOCATED'
        """)

        allocation = {}

        for process_id, resource_id, units in cursor.fetchall():

            if process_id not in allocation:
                allocation[process_id] = {}

            allocation[process_id][resource_id] = units

        # -----------------------------------------
        # BUILD MAXIMUM MATRIX
        # -----------------------------------------

               # -----------------------------------------
        # BUILD MAXIMUM MATRIX
        # -----------------------------------------

        maximum = self.build_maximum_matrix()
        cursor.close()

        banker_result = self.banker.check_safe_state(

            allocation,
            maximum,
            available

        )

        resolver_result = self.resolver.resolve(

            banker_result

        )

        return {

            "success": True,

            "deadlock": banker_result["deadlock"],

            "safe": banker_result["safe"],

            "safe_sequence": banker_result["safe_sequence"],

            "status": resolver_result["status"],

            "message": resolver_result["message"]

        }