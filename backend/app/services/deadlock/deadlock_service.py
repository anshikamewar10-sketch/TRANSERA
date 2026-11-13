
"""
---------------------------------------------------------
Deadlock Service
---------------------------------------------------------
Purpose:
Banker's safety checking and actual deadlock detection.
---------------------------------------------------------
"""

from app.services.deadlock.common import DeadlockCommon
from app.services.deadlock.bankers import BankersAlgorithm
from app.services.deadlock.resolver import DeadlockResolver
from app.services.deadlock.detector import DeadlockDetector
from app.services.resource.resource_service import ResourceService


class DeadlockService(DeadlockCommon):

    def __init__(self):
        super().__init__()

        self.banker = BankersAlgorithm()
        self.resolver = DeadlockResolver()
        self.detector = DeadlockDetector()

    # =====================================================
    # LOAD RESOURCE DATA
    # =====================================================

    def load_resource_data(self):

        cursor = self.connection.cursor()

        try:
            cursor.execute("""
                SELECT RESOURCE_ID, AVAILABLE_UNITS
                FROM RESOURCES
            """)

            available = {
                rid: int(units)
                for rid, units in cursor.fetchall()
            }

            cursor.execute("""
                SELECT PROCESS_ID,
                       RESOURCE_ID,
                       SUM(ALLOCATED_UNITS)
                FROM RESOURCE_ALLOCATIONS
                WHERE ALLOCATION_STATUS = 'ALLOCATED'
                GROUP BY PROCESS_ID, RESOURCE_ID
            """)

            allocation = {}

            for pid, rid, units in cursor.fetchall():
                allocation.setdefault(pid, {})[rid] = int(units)

            cursor.execute("""
                SELECT PROCESS_ID,
                       RESOURCE_ID,
                       REQUESTED_UNITS
                FROM RESOURCE_REQUESTS
            """)

            requests = {}

            for pid, rid, units in cursor.fetchall():
                requests.setdefault(pid, {})[rid] = int(units)

            return available, allocation, requests

        finally:
            cursor.close()

    # =====================================================
    # EXISTING BANKER'S SAFETY CHECK
    # =====================================================

    def check_deadlock(self):

        available, allocation, requests = (
            self.load_resource_data()
        )

        maximum = self.build_maximum_matrix()

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

    # =====================================================
    # NEW: ACTUAL DEADLOCK DETECTION
    # =====================================================

    
    # =====================================================
    # DEADLOCK DETECTION + AUTOMATIC COMPLETION
    # =====================================================

    def detect_deadlock(self):

        available, allocation, requests = (
            self.load_resource_data()
        )

        result = self.detector.detect(
            available,
            allocation,
            requests
        )

        # ==========================================
        # SCENARIO B: DEADLOCK DETECTED
        # ==========================================

        if result["deadlock"]:

            return {
                "success": True,
                "deadlock": True,
                "deadlocked_processes":
                    result["deadlocked_processes"],
                "completion_sequence":
                    result["completion_sequence"],
                "status": "DEADLOCK_DETECTED",
                "message": (
                    "Deadlock detected. "
                    "Resolve deadlock to continue."
                )
            }

        # ==========================================
        # SCENARIO A: NO DEADLOCK
        # ==========================================

        resource_service = ResourceService()

        completion_result = (
            resource_service.complete_all_allocated()
        )

        return {
            "success": completion_result["success"],
            "deadlock": False,
            "deadlocked_processes": [],
            "completion_sequence":
                result["completion_sequence"],
            "status": (
                "NO_DEADLOCK_COMPLETED"
                if completion_result["success"]
                else "COMPLETION_PARTIAL_FAILURE"
            ),
            "completion_result": completion_result,
            "message": (
                "No deadlock detected. "
                "Allocated processes completed and resources released."
                if completion_result["success"]
                else "No deadlock detected, but some completions failed."
            )
        }
