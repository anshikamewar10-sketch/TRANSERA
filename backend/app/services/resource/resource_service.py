"""
---------------------------------------------------------
Resource Service
---------------------------------------------------------
Purpose:
Controls Resource Allocation and Waiting Queue.
---------------------------------------------------------
"""

from app.database.connection import get_connection

from app.services.resource.allocator import ResourceAllocator
from app.services.resource.waiting_queue import WaitingQueue


class ResourceService:

    def __init__(self):
    
          self.connection = get_connection()

          self.allocator = ResourceAllocator()
          self.waiting = WaitingQueue()

        # Share one Oracle connection
          self.allocator.connection = self.connection
          self.waiting.connection = self.connection
          self.allocator.deadlock_common.connection = self.connection

    # =====================================================
    # RESOURCE CENTER
    # =====================================================
    
    # =====================================================
    # SYNC OUTSTANDING RESOURCE REQUESTS
    # =====================================================

    def sync_resource_requests(self, process_id, requirements):

        cursor = self.connection.cursor()

        try:
            cursor.execute("""
                SELECT RESOURCE_ID, NVL(SUM(ALLOCATED_UNITS), 0)
                FROM RESOURCE_ALLOCATIONS
                WHERE PROCESS_ID = :1
                  AND ALLOCATION_STATUS = 'ALLOCATED'
                GROUP BY RESOURCE_ID
            """, (process_id,))

            held = {
                rid: int(units)
                for rid, units in cursor.fetchall()
            }

            cursor.execute("""
                DELETE FROM RESOURCE_REQUESTS
                WHERE PROCESS_ID = :1
            """, (process_id,))

            for resource_id, info in requirements.items():

                remaining = (
                    int(info["max_units"])
                    - held.get(resource_id, 0)
                )

                if remaining > 0:

                    cursor.execute("""
                        INSERT INTO RESOURCE_REQUESTS
                        (
                            PROCESS_ID,
                            RESOURCE_ID,
                            REQUESTED_UNITS
                        )
                        VALUES (:1, :2, :3)
                    """, (
                        process_id,
                        resource_id,
                        remaining
                    ))

        finally:
            cursor.close()

    
   
  
    # =====================================================
    # RESOURCE ALLOCATION + DEADLOCK INTEGRATION
    # =====================================================

    def manage_resources(self):

        cursor = self.connection.cursor()

        try:
            cursor.execute("""
                SELECT PROCESS_ID
                FROM PROCESSES
                WHERE PROCESS_STATE IN (
                    'AWAITING_RESOURCES',
                    'WAITING'
                )
                ORDER BY ARRIVAL_TIME, PROCESS_ID
            """)

            processes = [row[0] for row in cursor.fetchall()]

        finally:
            cursor.close()

        if not processes:
            return {
                "success": False,
                "message": "No processes awaiting resource allocation."
            }

        results = []

        for process_id in processes:

            try:
                requirements = (
                    self.allocator.get_process_requirements(process_id)
                )

                if not requirements:
                    self.connection.rollback()

                    results.append({
                        "process_id": process_id,
                        "status": "ERROR",
                        "message": "Resource requirements missing."
                    })
                    continue

                # ==========================================
                # ATTEMPT RESOURCE ALLOCATION
                # ==========================================

                allocation = self.allocator.allocate_resources(process_id)

                if not allocation["success"]:

                    if allocation.get("status") in ("UNSAFE", "WAITING"):

                        # Move process to WAITING
                        self.waiting.move_to_waiting(process_id)

                        # Record outstanding requests in Oracle
                        self.sync_resource_requests(
                            process_id,
                            requirements
                        )

                        # Commit WAITING state and requests together
                        self.connection.commit()

                        results.append({
                            "process_id": process_id,
                            "status": "WAITING",
                            "allocated_resources": [],
                            "waiting_resources": allocation.get(
                                "waiting_resources", []
                            ),
                            "message": allocation.get("message")
                        })

                    else:
                        self.connection.rollback()

                        results.append({
                            "process_id": process_id,
                            "status": "ERROR",
                            "message": allocation.get(
                                "message", "Allocation failed."
                            )
                        })

                    continue

                # ==========================================
                # READ ACTUAL ALLOCATED INSTANCES
                # ==========================================

                cursor = self.connection.cursor()

                try:
                    cursor.execute("""
                        SELECT RESOURCE_ID,
                               SUM(ALLOCATED_UNITS)
                        FROM RESOURCE_ALLOCATIONS
                        WHERE PROCESS_ID = :1
                          AND ALLOCATION_STATUS = 'ALLOCATED'
                        GROUP BY RESOURCE_ID
                    """, (process_id,))

                    held = {
                        rid: int(units)
                        for rid, units in cursor.fetchall()
                    }

                finally:
                    cursor.close()

                missing = []

                for resource_id, info in requirements.items():

                    remaining = (
                        int(info["max_units"])
                        - held.get(resource_id, 0)
                    )

                    if remaining > 0:
                        missing.append({
                            "resource_name": info["resource_name"],
                            "units_needed": remaining
                        })

                # ==========================================
                # UPDATE PROCESS STATE
                # ==========================================

                status = "WAITING" if missing else "ALLOCATED"

                cursor = self.connection.cursor()

                try:
                    cursor.execute("""
                        UPDATE PROCESSES
                        SET PROCESS_STATE = :1
                        WHERE PROCESS_ID = :2
                          AND PROCESS_STATE IN (
                              'AWAITING_RESOURCES',
                              'WAITING'
                          )
                    """, (status, process_id))

                    if cursor.rowcount != 1:
                        raise RuntimeError(
                            "Process state update failed."
                        )

                finally:
                    cursor.close()

                # ==========================================
                # SYNCHRONIZE DEADLOCK REQUESTS
                # ==========================================

                if status == "WAITING":

                    self.sync_resource_requests(
                        process_id,
                        requirements
                    )

                else:

                    cursor = self.connection.cursor()

                    try:
                        cursor.execute("""
                            DELETE FROM RESOURCE_REQUESTS
                            WHERE PROCESS_ID = :1
                        """, (process_id,))

                    finally:
                        cursor.close()

                # ==========================================
                # SAVE EVERYTHING TO ORACLE
                # ==========================================

                self.connection.commit()

                results.append({
                    "process_id": process_id,
                    "status": status,
                    "allocated_resources": allocation.get(
                        "allocated_resources", []
                    ),
                    "waiting_resources": missing
                })

            except Exception as error:

                self.connection.rollback()

                results.append({
                    "process_id": process_id,
                    "status": "ERROR",
                    "message": str(error)
                })

        return {
            "success": True,
            "total_processed": len(results),
            "results": results,
            "waiting_queue": self.waiting.get_waiting_queue(),
            "message": "Resource Allocation Processing Completed."
        }





    
    # ==========================================
    # COMPLETE PROCESS AND RELEASE RESOURCES
    # ==========================================

    def complete_and_release(self, process_id, auto_retry=True):

        cursor = self.connection.cursor()

        try:
            cursor.execute("""
                SELECT OPERATION_ID, PROCESS_STATE
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

            operation_id, state = row

            if state != "ALLOCATED":
                self.connection.rollback()
                return {
                    "success": False,
                    "message": "Process is not in ALLOCATED state."
                }

            # Release all allocated resource instances
            result = self.allocator.release_resources(process_id)

            if not result["success"]:
                self.connection.rollback()
                return result

            # Update process state
            cursor.execute("""
                UPDATE PROCESSES
                SET PROCESS_STATE = 'TERMINATED'
                WHERE PROCESS_ID = :1
                  AND PROCESS_STATE = 'ALLOCATED'
            """, (process_id,))

            if cursor.rowcount != 1:
                raise RuntimeError("Process completion failed.")

            # Update business operation
            cursor.execute("""
                UPDATE BUSINESS_OPERATIONS
                SET BUSINESS_STATUS = 'COMPLETED'
                WHERE OPERATION_ID = :1
                  AND BUSINESS_STATUS = 'PROCESSING'
            """, (operation_id,))

            if cursor.rowcount != 1:
                raise RuntimeError("Business operation completion failed.")

            # Save all changes together
            cursor.execute("""
                DELETE FROM RESOURCE_REQUESTS
                WHERE PROCESS_ID = :1
                """, (process_id,))
            
            # Save completion and resource release together
            self.connection.commit()

                        # Automatically retry only when requested
            retry_result = None

            if auto_retry:
                try:
                    retry_result = self.manage_resources()

                except Exception as retry_error:
                    self.connection.rollback()

                    retry_result = {
                        "success": False,
                        "message": str(retry_error)
                    }

            return {
                "success": True,
                "process_id": process_id,
                "operation_id": operation_id,
                "process_state": "TERMINATED",
                "business_status": "COMPLETED",
                "released_resources": result["released_resources"],
                "retry_result": retry_result,
                "message": (
                    "Process completed, resources released, "
                    "and waiting processes checked."
                )
            }


        except Exception:
            self.connection.rollback()
            raise

        finally:
            cursor.close()



    
    # =====================================================
    # COMPLETE ALL ALLOCATED PROCESSES
    # =====================================================

    def complete_all_allocated(self):

        cursor = self.connection.cursor()

        try:
            cursor.execute("""
                SELECT PROCESS_ID
                FROM PROCESSES
                WHERE PROCESS_STATE = 'ALLOCATED'
                ORDER BY ARRIVAL_TIME, PROCESS_ID
            """)

            process_ids = [
                row[0] for row in cursor.fetchall()
            ]

        finally:
            cursor.close()

        if not process_ids:
            return {
                "success": True,
                "total_completed": 0,
                "completed_processes": [],
                "message": "No allocated processes awaiting completion."
            }

        completed = []
        errors = []

        for process_id in process_ids:

            try:
                # Reuse existing completion and release logic
                result = self.complete_and_release(
                    process_id,
                    auto_retry=False
                )

                if result["success"]:
                    completed.append({
                        "process_id": process_id,
                        "operation_id": result["operation_id"],
                        "process_state": "TERMINATED",
                        "business_status": "COMPLETED",
                        "released_resources": result["released_resources"]
                    })

                else:
                    errors.append({
                        "process_id": process_id,
                        "message": result.get(
                            "message", "Completion failed."
                        )
                    })

            except Exception as error:
                self.connection.rollback()

                errors.append({
                    "process_id": process_id,
                    "message": str(error)
                })

        return {
            "success": len(errors) == 0,
            "total_completed": len(completed),
            "completed_processes": completed,
            "errors": errors,
            "message": (
                "Allocated processes completed and resources released."
                if not errors
                else "Some processes could not be completed."
            )
        }

     # =====================================================

    # RESOURCE HISTORY
    # =====================================================

    def get_resource_history(self):

        cursor = self.allocator.connection.cursor()

        cursor.execute("""
            SELECT
                RA.PROCESS_ID,
                R.RESOURCE_NAME,
                RA.ALLOCATION_STATUS,
                RA.ALLOCATION_TIME
            FROM RESOURCE_ALLOCATIONS RA
            JOIN RESOURCES R
            ON RA.RESOURCE_ID = R.RESOURCE_ID
            ORDER BY RA.ALLOCATION_TIME DESC
            """)

        rows = cursor.fetchall()

        cursor.close()

        history = []

        for row in rows:

            history.append(
                {
                    "process_id": row[0],
                    "resource_name": row[1],
                    "allocation_status": row[2],
                    "allocation_time": row[3].strftime("%Y-%m-%d %H:%M:%S"),
                }
            )

        return {"success": True, "history": history}
