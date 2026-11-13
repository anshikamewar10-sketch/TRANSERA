
"""
Deadlock Recovery Service

Detects a deadlock, selects a victim, releases its
resources, and records recovery in Oracle.

Victim is suspended for controlled recovery.
Business operation is NOT marked COMPLETED.
"""

from app.database.connection import get_connection
from app.services.deadlock.detector import DeadlockDetector


class DeadlockRecoveryService:

    def __init__(self):
        self.connection = get_connection()
        self.detector = DeadlockDetector()

    def recover_deadlock(self):

        cursor = self.connection.cursor()

        try:
            # Serialize resource modifications.
            cursor.execute("""
                LOCK TABLE RESOURCES IN EXCLUSIVE MODE
            """)

            cursor.execute("""
                SELECT RESOURCE_ID, AVAILABLE_UNITS
                FROM RESOURCES
            """)

            available = {
                rid: int(units)
                for rid, units in cursor.fetchall()
            }

            cursor.execute("""
                SELECT PROCESS_ID, RESOURCE_ID,
                       SUM(ALLOCATED_UNITS)
                FROM RESOURCE_ALLOCATIONS
                WHERE ALLOCATION_STATUS = 'ALLOCATED'
                GROUP BY PROCESS_ID, RESOURCE_ID
            """)

            allocation = {}

            for pid, rid, units in cursor.fetchall():
                allocation.setdefault(pid, {})[rid] = int(units)

            cursor.execute("""
                SELECT PROCESS_ID, RESOURCE_ID,
                       REQUESTED_UNITS
                FROM RESOURCE_REQUESTS
            """)

            requests = {}

            for pid, rid, units in cursor.fetchall():
                requests.setdefault(pid, {})[rid] = int(units)

            result = self.detector.detect(
                available, allocation, requests
            )

            if not result["deadlock"]:
                self.connection.rollback()
                return {
                    "success": True,
                    "deadlock": False,
                    "resolved": False,
                    "message": "No deadlock detected."
                }

            deadlocked = result["deadlocked_processes"]

            # Prefer a victim holding fewer resource units.
            victim = min(
                deadlocked,
                key=lambda pid: (
                    sum(allocation.get(pid, {}).values()),
                    pid
                )
            )

            cursor.execute("""
                SELECT ALLOCATION_ID, RESOURCE_ID,
                       ALLOCATED_UNITS
                FROM RESOURCE_ALLOCATIONS
                WHERE PROCESS_ID = :1
                  AND ALLOCATION_STATUS = 'ALLOCATED'
                FOR UPDATE
            """, (victim,))

            rows = cursor.fetchall()
            released = []

            for allocation_id, rid, units in rows:

                units = int(units)

                cursor.execute("""
                    UPDATE RESOURCES
                    SET AVAILABLE_UNITS = AVAILABLE_UNITS + :1
                    WHERE RESOURCE_ID = :2
                      AND AVAILABLE_UNITS + :1 <= TOTAL_UNITS
                """, (units, rid))

                if cursor.rowcount != 1:
                    raise RuntimeError(
                        "Resource release capacity check failed."
                    )

                cursor.execute("""
                    UPDATE RESOURCE_ALLOCATIONS
                    SET ALLOCATION_STATUS = 'RELEASED'
                    WHERE ALLOCATION_ID = :1
                      AND ALLOCATION_STATUS = 'ALLOCATED'
                """, (allocation_id,))

                if cursor.rowcount != 1:
                    raise RuntimeError(
                        "Failed to mark allocation RELEASED."
                    )

                released.append({
                    "resource_id": rid,
                    "units_released": units
                })

            # Remove victim's outstanding requests.
            cursor.execute("""
                DELETE FROM RESOURCE_REQUESTS
                WHERE PROCESS_ID = :1
            """, (victim,))

            # Suspend the victim rather than falsely completing it.
            cursor.execute("""
                UPDATE PROCESSES
                SET PROCESS_STATE = 'RECOVERY_PENDING'
                WHERE PROCESS_ID = :1
                  AND PROCESS_STATE = 'WAITING'
            """, (victim,))

            if cursor.rowcount != 1:
                raise RuntimeError(
                    "Victim process state could not be updated."
                )

            cursor.execute("""
                INSERT INTO DEADLOCK_RECOVERY_LOG
                (
                    RECOVERY_ID,
                    VICTIM_PROCESS_ID,
                    DETAILS
                )
                VALUES
                (
                    DEADLOCK_RECOVERY_SEQ.NEXTVAL,
                    :1,
                    :2
                )
            """, (
                victim,
                "Victim suspended and allocated resources released."
            ))

            
            # Commit victim recovery and resource release
            self.connection.commit()

            # Prepare victim for future allocation
            # without requiring a separate Resume button.
            resume_result = self.resume_process(victim)

            return {
                "success": resume_result["success"],
                "deadlock": True,
                "resolved": resume_result["success"],
                "victim_process_id": victim,
                "process_state": (
                    "WAITING"
                    if resume_result["success"]
                    else "RECOVERY_PENDING"
                ),
                "released_resources": released,
                "resume_result": resume_result,
                "message": (
                    "Deadlock recovery completed. "
                    "Victim returned to WAITING for future allocation."
                    if resume_result["success"]
                    else "Resources released, but victim resumption failed."
                )
            }


        except Exception:
            self.connection.rollback()
            raise

        finally:
            cursor.close()
   
   
   
   
    # =====================================================
    # RESUME RECOVERY VICTIM
    # =====================================================

    def resume_process(self, process_id):

        cursor = self.connection.cursor()

        try:
            cursor.execute("""
                SELECT PROCESS_STATE
                FROM PROCESSES
                WHERE PROCESS_ID = :1
                FOR UPDATE
            """, (process_id,))

            row = cursor.fetchone()

            if row is None:
                self.connection.rollback()
                return {
                    "success": False,
                    "message": "Process not found."
                }

            if row[0] != "RECOVERY_PENDING":
                self.connection.rollback()
                return {
                    "success": False,
                    "message": "Process is not pending recovery."
                }

            # Return victim to the resource waiting queue.
            cursor.execute("""
                UPDATE PROCESSES
                SET PROCESS_STATE = 'WAITING'
                WHERE PROCESS_ID = :1
            """, (process_id,))

            # Rebuild outstanding resource requests.
            cursor.execute("""
                DELETE FROM RESOURCE_REQUESTS
                WHERE PROCESS_ID = :1
            """, (process_id,))

            cursor.execute("""
                INSERT INTO RESOURCE_REQUESTS
                (PROCESS_ID, RESOURCE_ID, REQUESTED_UNITS)
                SELECT
                    PR.PROCESS_ID,
                    PR.RESOURCE_ID,
                    PR.MAX_UNITS - NVL(A.HELD, 0)
                FROM PROCESS_RESOURCE_REQUIREMENTS PR
                LEFT JOIN (
                    SELECT PROCESS_ID,
                           RESOURCE_ID,
                           SUM(ALLOCATED_UNITS) AS HELD
                    FROM RESOURCE_ALLOCATIONS
                    WHERE ALLOCATION_STATUS = 'ALLOCATED'
                    GROUP BY PROCESS_ID, RESOURCE_ID
                ) A
                    ON PR.PROCESS_ID = A.PROCESS_ID
                   AND PR.RESOURCE_ID = A.RESOURCE_ID
                WHERE PR.PROCESS_ID = :1
                  AND PR.MAX_UNITS > NVL(A.HELD, 0)
            """, (process_id,))

            self.connection.commit()

            return {
                "success": True,
                "process_id": process_id,
                "process_state": "WAITING",
                "message": "Recovery victim returned to waiting queue."
            }

        except Exception:
            self.connection.rollback()
            raise

        finally:
            cursor.close()
