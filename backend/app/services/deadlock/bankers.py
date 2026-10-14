"""
---------------------------------------------------------
Banker's Algorithm
---------------------------------------------------------
Purpose:
Checks whether the system is in a SAFE state.
---------------------------------------------------------
"""


class BankersAlgorithm:

    def check_safe_state(self,
                         allocation,
                         maximum,
                         available):

        processes = list(maximum.keys())

        finish = {}

        safe_sequence = []

        # -----------------------------------------
        # INITIALIZE
        # -----------------------------------------

        for process in processes:

            finish[process] = False

        work = available.copy()

        # -----------------------------------------
        # NEED MATRIX
        # -----------------------------------------

        need = {}

        for process in processes:

            need[process] = {}

            for resource in maximum[process]:

                allocated = allocation.get(process, {}).get(resource, 0)

                need[process][resource] = (
                    maximum[process][resource] - allocated
                )

        # -----------------------------------------
        # SAFETY ALGORITHM
        # -----------------------------------------

        changed = True

        while changed:

            changed = False

            for process in processes:

                if finish[process]:

                    continue

                possible = True

                for resource in need[process]:

                    if need[process][resource] > work.get(resource, 0):

                        possible = False
                        break

                if possible:

                    for resource in allocation.get(process, {}):

                        work[resource] += allocation[process][resource]

                    finish[process] = True

                    safe_sequence.append(process)

                    changed = True

        # -----------------------------------------
        # RESULT
        # -----------------------------------------

        deadlock = False

        for process in finish:

            if finish[process] is False:

                deadlock = True
                break

        return {

            "safe": not deadlock,

            "deadlock": deadlock,

            "safe_sequence": safe_sequence

        }