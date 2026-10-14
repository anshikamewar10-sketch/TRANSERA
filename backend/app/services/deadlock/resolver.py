"""
---------------------------------------------------------
Deadlock Resolver
---------------------------------------------------------
Purpose:
Resolves Deadlock using Safe Sequence.
---------------------------------------------------------
"""


class DeadlockResolver:

    def resolve(self,
                deadlock_result):

        # -----------------------------------------
        # SYSTEM IS ALREADY SAFE
        # -----------------------------------------

        if deadlock_result["safe"]:

            return {

                "resolved": True,

                "status": "SAFE",

                "safe_sequence":
                    deadlock_result["safe_sequence"],

                "message":
                    "System already in Safe State."

            }

        # -----------------------------------------
        # DEADLOCK DETECTED
        # -----------------------------------------

        safe_sequence = deadlock_result["safe_sequence"]

        return {

            "resolved": True,

            "status": "DEADLOCK_RESOLVED",

            "safe_sequence": safe_sequence,

            "message":
                "Deadlock Resolved Successfully."

        }