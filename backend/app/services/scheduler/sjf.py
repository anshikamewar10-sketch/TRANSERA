"""
---------------------------------------------------------
SJF Scheduling Algorithm
---------------------------------------------------------
Purpose:
Executes Shortest Job First Scheduling.
---------------------------------------------------------
"""

from app.services.scheduler.common import SchedulerCommon


class SJF(SchedulerCommon):

    def run(self, ready_queue):

        gantt_chart = []

        if len(ready_queue) == 0:

            return {
                "success": False,
                "message": "No READY Processes Found."
            }

        # ==========================================
        # SORT BY BURST TIME
        # ==========================================

        ready_queue.sort(
            key=lambda process: process["burst_time"]
        )

        for process in ready_queue:

            process_id = process["process_id"]

            self.execute_process(
                process_id,
                gantt_chart
            )

        return {

            "success": True,

            "algorithm": "SJF",

            "gantt_chart": gantt_chart,

            "running_process": None,

            "ready_queue": [],

            "status": "Scheduling Completed.",

            "message": "SJF Scheduling Completed Successfully."

        }