"""
---------------------------------------------------------
Priority Scheduling Algorithm
---------------------------------------------------------
Purpose:
Executes Priority Scheduling.
---------------------------------------------------------
"""

from app.services.scheduler.common import SchedulerCommon


class PriorityScheduling(SchedulerCommon):

    def run(self, ready_queue):

        gantt_chart = []

        if len(ready_queue) == 0:

            return {
                "success": False,
                "message": "No READY Processes Found."
            }

        # ==========================================
        # SORT BY PRIORITY
        # Smaller number = Higher Priority
        # ==========================================

        ready_queue.sort(
            key=lambda process: process["priority"]
        )

        for process in ready_queue:

            process_id = process["process_id"]

            self.execute_process(
                process_id,
                gantt_chart
            )

        return {

            "success": True,

            "algorithm": "Priority",

            "gantt_chart": gantt_chart,

            "running_process": None,

            "ready_queue": [],

            "status": "Scheduling Completed.",

            "message": "Priority Scheduling Completed Successfully."

        }