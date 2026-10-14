"""
----------------------------------------------------
Process Service
Purpose :
1. Create Process
2. View Processes
----------------------------------------------------
"""

from app.database.connection import get_connection


def get_all_processes():

    connection = get_connection()

    if connection is None:
        return

    cursor = connection.cursor()

    query = """
    SELECT
        PROCESS_ID,
        OPERATION_ID,
        PROCESS_STATE,
        ARRIVAL_TIME,
        BURST_TIME,
        PRIORITY
    FROM PROCESSES
    ORDER BY PROCESS_ID
    """

    cursor.execute(query)

    rows = cursor.fetchall()

    print("\n========== PROCESSES ==========\n")

    for row in rows:

        print(
            f"{row[0]} | {row[1]} | {row[2]} | Arrival:{row[3]} | Burst:{row[4]} | Priority:{row[5]}"
        )

    print("\n=================================\n")

    cursor.close()
    connection.close()


if __name__ == "__main__":

    get_all_processes()