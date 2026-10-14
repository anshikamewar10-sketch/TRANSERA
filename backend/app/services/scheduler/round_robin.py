"""
---------------------------------------------------------
Round Robin Scheduling Algorithm
---------------------------------------------------------
Purpose:
Executes Round Robin Scheduling.
---------------------------------------------------------
"""

from app.services.scheduler.common import SchedulerCommon


class RoundRobin(SchedulerCommon):

    def run(self, ready_queue):

        gantt_chart = []

        if len(ready_queue) == 0:

            return {
                "success": False,
                "message": "No READY Processes Found."
            }

        quantum = 2

        queue = ready_queue.copy()

        while len(queue) > 0:

            process = queue.pop(0)

            process_id = process["process_id"]

            burst_time = process["burst_time"]

            self.update_process_state(
                process_id,
                "RUNNING"
            )

            self.write_log(
                process_id,
                "RUNNING",
                "CPU Allocated"
            )

            if burst_time > quantum:

                burst_time -= quantum

                process["burst_time"] = burst_time

                gantt_chart.append(process_id)

                self.update_process_state(
                    process_id,
                    "READY"
                )

                self.write_log(
                    process_id,
                    "CONTEXT_SWITCH",
                    "Quantum Expired"
                )

                queue.append(process)

            else:

                self.execute_process(
                    process_id,
                    gantt_chart
                )

        return {

            "success": True,

            "algorithm": "Round Robin",

            "gantt_chart": gantt_chart,

            "running_process": None,

            "ready_queue": [],

            "status": "Scheduling Completed.",

            "message": "Round Robin Scheduling Completed Successfully."

        }