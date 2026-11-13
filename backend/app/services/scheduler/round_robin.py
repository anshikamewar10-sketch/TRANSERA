
"""
TRANSERA - Round Robin Scheduling
Arrival-aware, preemptive CPU scheduling.
"""

from collections import deque


class RoundRobin:

    QUANTUM = 2

    def run(self, ready_queue):

        if not ready_queue:
            return {
                "success": False,
                "message": "No READY Processes Found."
            }

        processes = sorted(
            [dict(p) for p in ready_queue],
            key=lambda p: (
                float(p["arrival_time"]),
                p["process_id"]
            )
        )

        remaining = {
            p["process_id"]: float(
                p.get("remaining_burst_time")
                if p.get("remaining_burst_time") is not None
                else p["burst_time"]
            )
            for p in processes
        }

        quantum = self.QUANTUM
        queue = deque()
        timeline = []

        current_time = float(processes[0]["arrival_time"])
        next_arrival = 0

        def enqueue_arrivals():
            nonlocal next_arrival

            while (
                next_arrival < len(processes)
                and float(
                    processes[next_arrival]["arrival_time"]
                ) <= current_time
            ):
                queue.append(processes[next_arrival])
                next_arrival += 1

        enqueue_arrivals()

        while queue or next_arrival < len(processes):

            if not queue:
                current_time = float(
                    processes[next_arrival]["arrival_time"]
                )
                enqueue_arrivals()

            process = queue.popleft()
            pid = process["process_id"]

            duration = min(quantum, remaining[pid])

            start = current_time
            current_time += duration
            remaining[pid] -= duration

            enqueue_arrivals()

            completed = remaining[pid] <= 0

            timeline.append({
                "process_id": pid,
                "start_time": start,
                "end_time": current_time,
                "duration": duration,
                "remaining_after": max(0, remaining[pid]),
                "completed": completed
            })

            if not completed:
                queue.append(process)

        return {
            "success": True,
            "algorithm": "ROUND_ROBIN",
            "time_quantum": quantum,
            "ready_queue": processes,
            "gantt_chart": timeline,
            "running_process": None,
            "status": "Ready For Execution",
            "message": "Round Robin execution sequence generated."
        }
