"""
---------------------------------------------------------
FCFS Scheduling Algorithm
---------------------------------------------------------
Purpose:
Returns the FCFS execution order.
Actual execution and visualization will be handled
by the frontend.
---------------------------------------------------------
"""

from app.services.scheduler.common import SchedulerCommon


class FCFS(SchedulerCommon):

    def run(self, ready_queue):

        if len(ready_queue) == 0:

            return {
                "success": False,
                "message": "No READY Processes Found."
            }

        gantt_chart = []

        for process in ready_queue:

            gantt_chart.append({

                "process_id": process["process_id"],

                "arrival_time": process["arrival_time"],

                "priority": process["priority"],

                "burst_time": process["burst_time"]

            })

        return {

            "success": True,

            "algorithm": "FCFS",

            "gantt_chart": gantt_chart,

            "running_process": None,

            "ready_queue": ready_queue,

            "status": "Ready For Execution",

            "message": "FCFS Order Generated Successfully."

        }