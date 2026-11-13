
"""
---------------------------------------------------------
Deadlock Detector
---------------------------------------------------------
Purpose:
Detects deadlocked processes using current resource
allocations, outstanding requests and available units.

Supports multiple instances of each resource type.
Does not modify Oracle.
---------------------------------------------------------
"""


class DeadlockDetector:

    def detect(self, available, allocation, requests):

        # Make sure all processes are considered
        processes = sorted(
            set(allocation.keys()) | set(requests.keys())
        )

        work = {
            resource_id: int(units)
            for resource_id, units in available.items()
        }

        finish = {}
        completion_sequence = []

        # Processes holding no resources cannot be
        # part of a resource-holding deadlock cycle.
        for process_id in processes:

            held = allocation.get(process_id, {})

            finish[process_id] = not any(
                units > 0 for units in held.values()
            )

        # ==========================================
        # DEADLOCK DETECTION ALGORITHM
        # ==========================================

        changed = True

        while changed:

            changed = False

            for process_id in processes:

                if finish[process_id]:
                    continue

                required = requests.get(process_id, {})

                can_proceed = all(
                    int(units) <= work.get(resource_id, 0)
                    for resource_id, units in required.items()
                )

                if can_proceed:

                    # Simulate completion and resource release
                    for resource_id, units in allocation.get(
                        process_id, {}
                    ).items():

                        work[resource_id] = (
                            work.get(resource_id, 0)
                            + int(units)
                        )

                    finish[process_id] = True
                    completion_sequence.append(process_id)
                    changed = True

        deadlocked = [
            process_id
            for process_id in processes
            if not finish[process_id]
        ]

        return {
            "deadlock": len(deadlocked) > 0,
            "deadlocked_processes": deadlocked,
            "completion_sequence": completion_sequence,
            "available_after_check": work
        }
