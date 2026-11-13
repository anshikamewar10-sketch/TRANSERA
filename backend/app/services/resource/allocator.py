
"""
Resource Allocator
Multiple-instance allocation with Banker's safety check.
"""

from app.services.resource.common import ResourceCommon
from app.services.deadlock.bankers import BankersAlgorithm
from app.services.deadlock.common import DeadlockCommon


class ResourceAllocator(ResourceCommon):

    def __init__(self):
        super().__init__()
        self.banker = BankersAlgorithm()
        self.deadlock_common = DeadlockCommon()

    def allocate_resources(self, process_id):

        cursor = self.connection.cursor()

        try:
            # Serialize allocation requests using the resource table.
            # This is suitable for our single-database demo.
            cursor.execute("""
                LOCK TABLE RESOURCES IN EXCLUSIVE MODE
            """)

            cursor.execute("""
                SELECT PROCESS_STATE
                FROM PROCESSES
                WHERE PROCESS_ID = :1
            """, (process_id,))

            row = cursor.fetchone()

            if row is None:
                self.connection.rollback()
                return {
                    "success": False,
                    "status": "ERROR",
                    "message": "Process not found."
                }

            if row[0] not in ("AWAITING_RESOURCES", "WAITING"):
                self.connection.rollback()
                return {
                    "success": False,
                    "status": "ERROR",
                    "message": "Process is not awaiting resources."
                }

            requirements = self.get_process_requirements(process_id)

            if not requirements:
                self.connection.rollback()
                return {
                    "success": False,
                    "status": "ERROR",
                    "message": "Resource requirements are missing."
                }

            # Read existing allocations.
            cursor.execute("""
                SELECT RESOURCE_ID, SUM(ALLOCATED_UNITS)
                FROM RESOURCE_ALLOCATIONS
                WHERE PROCESS_ID = :1
                  AND ALLOCATION_STATUS = 'ALLOCATED'
                GROUP BY RESOURCE_ID
            """, (process_id,))

            existing = {
                rid: int(units)
                for rid, units in cursor.fetchall()
            }

            # Determine remaining requirements.
            requests = {}

            for rid, info in requirements.items():

                max_units = int(info["max_units"])
                held = existing.get(rid, 0)

                if held > max_units:
                    self.connection.rollback()
                    return {
                        "success": False,
                        "status": "ERROR",
                        "message": "Allocation exceeds maximum claim."
                    }

                remaining = max_units - held

                if remaining > 0:
                    requests[rid] = remaining

            # Read resource availability.
            cursor.execute("""
                SELECT RESOURCE_ID, AVAILABLE_UNITS
                FROM RESOURCES
            """)

            available = {
                rid: int(units)
                for rid, units in cursor.fetchall()
            }

            # Check whether all requested units are available.
            insufficient = []

            for rid, units in requests.items():

                if available.get(rid, 0) < units:
                    insufficient.append({
                        "resource_name":
                            requirements[rid]["resource_name"],
                        "units_needed": units,
                        "available_units": available.get(rid, 0)
                    })

            if insufficient:
                self.connection.rollback()
                return {
                    "success": False,
                    "process_id": process_id,
                    "status": "WAITING",
                    "allocated_resources": [],
                    "waiting_resources": insufficient,
                    "message": "Insufficient resource instances."
                }

            # Read maximum claims.
            maximum = self.deadlock_common.build_maximum_matrix()

            if process_id not in maximum:
                self.connection.rollback()
                return {
                    "success": False,
                    "status": "ERROR",
                    "message": "Process missing from maximum matrix."
                }

            # Read all current allocations.
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

            # Simulate the proposed allocation in memory.
            tentative_available = available.copy()

            tentative_allocation = {
                pid: values.copy()
                for pid, values in allocation.items()
            }

            tentative_allocation.setdefault(process_id, {})

            for rid, units in requests.items():

                tentative_available[rid] -= units

                tentative_allocation[process_id][rid] = (
                    tentative_allocation[process_id].get(rid, 0)
                    + units
                )

            # Banker's safety check before database changes.
            result = self.banker.check_safe_state(
                tentative_allocation,
                maximum,
                tentative_available
            )

            if not result["safe"]:
                self.connection.rollback()
                return {
                    "success": False,
                    "process_id": process_id,
                    "status": "WAITING",
                    "allocated_resources": [],
                    "waiting_resources": [
                        {
                            "resource_name":
                                requirements[rid]["resource_name"],
                            "units_needed": units
                        }
                        for rid, units in requests.items()
                    ],
                    "message": "Request rejected: unsafe state."
                }

            # Grant the safe request.
            allocated = []

            for rid, units in requests.items():

                cursor.execute("""
                    UPDATE RESOURCES
                    SET AVAILABLE_UNITS = AVAILABLE_UNITS - :1
                    WHERE RESOURCE_ID = :2
                      AND AVAILABLE_UNITS >= :1
                """, (units, rid))

                if cursor.rowcount != 1:
                    raise RuntimeError(
                        "Resource availability changed."
                    )

                cursor.execute("""
                    SELECT NVL(
                        MAX(
                       CASE
                       WHEN REGEXP_LIKE(ALLOCATION_ID, '^RA[0-9]+$')
                       THEN TO_NUMBER(SUBSTR(ALLOCATION_ID, 3))
                       ELSE NULL
                        END
                         ),
                      0
                           ) + 1
                     FROM RESOURCE_ALLOCATIONS
                        """)

                next_id = int(cursor.fetchone()[0])
                cursor.execute("""
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
                        :1, :2, :3, :4,
                        'ALLOCATED',
                        CURRENT_TIMESTAMP
                    )
                """, (
                    f"RA{next_id:03d}",
                    process_id,
                    rid,
                    units
                ))

                allocated.append({
                    "resource_name":
                        requirements[rid]["resource_name"],
                    "units": units
                })

         

            return {
                "success": True,
                "process_id": process_id,
                "status": "ALLOCATED",
                "allocated_resources": allocated,
                "waiting_resources": [],
                "safe_sequence": result["safe_sequence"],
                "message": "Resources allocated safely."
            }

        except Exception:
            self.connection.rollback()
            raise

        finally:
            cursor.close()
