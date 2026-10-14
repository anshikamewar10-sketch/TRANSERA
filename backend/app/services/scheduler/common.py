"""
---------------------------------------------------------
Scheduler Common Functions
---------------------------------------------------------
Purpose:
Shared functions used by all scheduling algorithms.
---------------------------------------------------------
"""

import time

from app.database.connection import get_connection


class SchedulerCommon:

    def __init__(self):

        self.connection = get_connection()

    # ==============================================
    # UPDATE PROCESS STATE
    # ==============================================

    def update_process_state(self,
                             process_id,
                             process_state):

        cursor = self.connection.cursor()

        # -----------------------------------------
        # UPDATE PROCESS STATE
        # -----------------------------------------

        cursor.execute(
            """
            UPDATE PROCESSES
            SET PROCESS_STATE = :state
            WHERE PROCESS_ID = :pid
            """,
            {
                "state": process_state,
                "pid": process_id
            }
        )

        # -----------------------------------------
        # UPDATE BUSINESS OPERATION STATUS
        # -----------------------------------------

        if process_state == "RUNNING":
            business_status = "PROCESSING"

        elif process_state == "COMPLETED":
            business_status = "COMPLETED"

        else:
            business_status = "READY"

        cursor.execute(
            """
            UPDATE BUSINESS_OPERATIONS
            SET BUSINESS_STATUS = :status
            WHERE OPERATION_ID =
            (
                SELECT OPERATION_ID
                FROM PROCESSES
                WHERE PROCESS_ID = :pid
            )
            """,
            {
                "status": business_status,
                "pid": process_id
            }
        )

        self.connection.commit()

        cursor.close()

    # ==============================================
    # WRITE SYSTEM LOG
    # ==============================================

    def write_log(self,
                  process_id,
                  event,
                  description):

        cursor = self.connection.cursor()

        cursor.execute("""
            SELECT NVL(MAX(TO_NUMBER(SUBSTR(LOG_ID,3))),0)+1
            FROM SYSTEM_LOGS
        """)

        next_log = cursor.fetchone()[0]

        log_id = f"SL{next_log:03d}"

        cursor.execute(
            """
            INSERT INTO SYSTEM_LOGS
            (
                LOG_ID,
                PROCESS_ID,
                EVENT_TYPE,
                DESCRIPTION,
                EVENT_TIME
            )
            VALUES
            (
                :1,
                :2,
                :3,
                :4,
                CURRENT_TIMESTAMP
            )
            """,
            (
                log_id,
                process_id,
                event,
                description
            )
        )

        self.connection.commit()

        cursor.close()

    # ==============================================
    # EXECUTE PROCESS
    # ==============================================

        # ==============================================
    # EXECUTE PROCESS
    # ==============================================

        # ==============================================
    # EXECUTE PROCESS
    # ==============================================

    def execute_process(self,
                        process_id,
                        gantt_chart):

        # -----------------------------------------
        # PROCESS ENTERS RUNNING STATE
        # -----------------------------------------

        self.update_process_state(
            process_id,
            "RUNNING"
        )

        self.write_log(
            process_id,
            "RUNNING",
            "CPU Allocated"
        )

        # -----------------------------------------
        # RESOURCE ALLOCATION
        # -----------------------------------------

        try:

            from app.services.resource.resource_service import ResourceService

            resource_service = ResourceService()

            resource_result = resource_service.manage_resources(
                process_id
            )

        except Exception as error:

            print("Resource Allocation Error :", error)

            resource_result = None

        # -----------------------------------------
        # DEADLOCK CHECK
        # -----------------------------------------

        try:

            from app.services.deadlock.deadlock_service import DeadlockService

            deadlock_service = DeadlockService()

            deadlock_result = deadlock_service.check_deadlock()

        except Exception as error:

            print("Deadlock Error :", error)

            deadlock_result = {
                "safe": True
            }

        # -----------------------------------------
        # EXECUTE ONLY IF SAFE
        # -----------------------------------------

        if deadlock_result["safe"]:

            time.sleep(1)

            gantt_chart.append(process_id)

        else:

            self.write_log(
                process_id,
                "WAITING",
                "Waiting due to Unsafe State"
            )

            return deadlock_result

        # -----------------------------------------
        # RELEASE RESOURCES
        # -----------------------------------------

        try:

            from app.services.resource.common import ResourceCommon

            resource_common = ResourceCommon()

            resource_common.release_resources(
                process_id
            )

        except Exception as error:

            print("Resource Release Error :", error)

        # -----------------------------------------
        # PROCESS COMPLETES
        # -----------------------------------------

        self.update_process_state(
            process_id,
            "COMPLETED"
        )

        self.write_log(
            process_id,
            "COMPLETED",
            "Execution Finished"
        )

        return {

            "resource": resource_result,

            "deadlock": deadlock_result

        }