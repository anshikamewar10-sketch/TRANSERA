
"""
TRANSERA - Shortest Job First Scheduling
Non-preemptive, arrival-aware scheduling.
"""


class SJF:

    def run(self, ready_queue):

        if not ready_queue:
            return {
                "success": False,
                "message": "No READY Processes Found."
            }

        remaining = [dict(p) for p in ready_queue]

        current_time = min(
            float(p["arrival_time"]) for p in remaining
        )

        scheduled = []
        gantt_chart = []

        while remaining:

            eligible = [
                p for p in remaining
                if float(p["arrival_time"]) <= current_time
            ]

            if not eligible:
                current_time = min(
                    float(p["arrival_time"])
                    for p in remaining
                )

                eligible = [
                    p for p in remaining
                    if float(p["arrival_time"]) <= current_time
                ]

            process = min(
                eligible,
                key=lambda p: (
                    float(p["burst_time"]),
                    float(p["arrival_time"]),
                    p["process_id"]
                )
            )

            start = current_time
            duration = float(process["burst_time"])
            current_time += duration

            scheduled.append(process)

            gantt_chart.append({
                "process_id": process["process_id"],
                "start_time": start,
                "end_time": current_time,
                "duration": duration
            })

            remaining.remove(process)

        return {
            "success": True,
            "algorithm": "SJF",
            "gantt_chart": gantt_chart,
            "running_process": None,
            "ready_queue": scheduled,
            "status": "Ready For Execution",
            "message": "SJF scheduling order generated."
        }
