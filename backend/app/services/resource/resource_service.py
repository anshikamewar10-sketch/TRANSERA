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

    # =====================================================
    # RESOURCE CENTER
    # =====================================================

    def manage_resources(self):
        
        cursor = self.connection.cursor()

        cursor.execute("""
        SELECT PROCESS_ID
        FROM PROCESSES
        WHERE PROCESS_STATE='RUNNING'
     """)

        rows = cursor.fetchall()

        print("RUNNING PROCESSES:", rows)

        if len(rows) == 0:

          cursor.close()

          return {
        "success": False,
        "message": "No Running Process Found."
    }
 
        process_id = rows[0][0]

        allocation = self.allocator.allocate_resources(process_id)

        if allocation["success"] is False:

            return allocation

        if len(allocation["waiting_resources"]) > 0:

            self.waiting.move_to_waiting(process_id)

            status = "WAITING"

        else:

            status = "ALLOCATED"

        waiting_queue = self.waiting.get_waiting_queue()

        return {

            "success": True,

            "process_id": process_id,

            "status": status,

            "allocated_resources":
                allocation["allocated_resources"],

            "waiting_resources":
                allocation["waiting_resources"],

            "waiting_queue":
                waiting_queue,

            "message":
                "Resource Allocation Completed."

        }
            # =====================================================
    # RESOURCE HISTORY
    # =====================================================

    def get_resource_history(self):
    
        cursor = self.allocator.connection.cursor()

        cursor.execute(
            """
            SELECT
                RA.PROCESS_ID,
                R.RESOURCE_NAME,
                RA.ALLOCATION_STATUS,
                RA.ALLOCATION_TIME
            FROM RESOURCE_ALLOCATIONS RA
            JOIN RESOURCES R
            ON RA.RESOURCE_ID = R.RESOURCE_ID
            ORDER BY RA.ALLOCATION_TIME DESC
            """
        )

        rows = cursor.fetchall()

        cursor.close()

        history = []

        for row in rows:

            history.append({

                "process_id": row[0],

                "resource_name": row[1],

                "allocation_status": row[2],

                "allocation_time": row[3].strftime("%Y-%m-%d %H:%M:%S")

            })

        return {

            "success": True,

            "history": history

        }