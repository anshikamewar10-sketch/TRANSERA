"""
---------------------------------------------------------
Waiting Queue Manager
---------------------------------------------------------
Purpose:
Moves processes to WAITING state when
required resources are unavailable.
---------------------------------------------------------
"""

from app.services.resource.common import ResourceCommon


class WaitingQueue(ResourceCommon):

    def move_to_waiting(self, process_id):

        cursor = self.connection.cursor()

        cursor.execute(
            """
            UPDATE PROCESSES
            SET PROCESS_STATE='WAITING'
            WHERE PROCESS_ID=:1
            """,
            (
                process_id,
            )
        )

        self.connection.commit()

        cursor.close()

        return {
            "success": True,
            "process_id": process_id,
            "status": "WAITING"
        }

    def get_waiting_queue(self):

        cursor = self.connection.cursor()

        cursor.execute(
            """
            SELECT
                PROCESS_ID,
                OPERATION_ID
            FROM PROCESSES
            WHERE PROCESS_STATE='WAITING'
            ORDER BY ARRIVAL_TIME
            """
        )

        rows = cursor.fetchall()

        cursor.close()

        waiting_queue = []

        for row in rows:

            waiting_queue.append(
                {
                    "process_id": row[0],
                    "operation_id": row[1]
                }
            )

        return waiting_queue