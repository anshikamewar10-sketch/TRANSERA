
"""
TRANSERA Analytics Service
Read-only Oracle SQL analytics.
"""

from app.database.connection import get_connection


class AnalyticsService:

    def _fetch_all(self, cursor, query):
        cursor.execute(query)
        columns = [col[0].lower() for col in cursor.description]

        return [
            {
                columns[i]: (
                    float(value)
                    if value is not None
                    and hasattr(value, "as_integer_ratio")
                    and not isinstance(value, (int, float, str))
                    else value
                )
                for i, value in enumerate(row)
            }
            for row in cursor.fetchall()
        ]

    def _fetch_one(self, cursor, query):
        rows = self._fetch_all(cursor, query)
        return rows[0] if rows else {}

    def get_dashboard(self):
        connection = get_connection()
        cursor = connection.cursor()

        try:
            operations = self._fetch_one(
                cursor,
                "SELECT * FROM VW_AN_OPERATION_SUMMARY"
            )

            processes = self._fetch_one(
                cursor,
                "SELECT * FROM VW_AN_PROCESS_SUMMARY"
            )

            process_states = self._fetch_all(
                cursor,
                """
                SELECT STATUS, TOTAL
                FROM VW_AN_PROCESS_STATES
                ORDER BY TOTAL DESC, STATUS
                """
            )

            departments = self._fetch_all(
                cursor,
                """
                SELECT *
                FROM VW_AN_DEPARTMENT_STATS
                ORDER BY TOTAL_OPERATIONS DESC, DEPARTMENT
                """
            )

            resources = self._fetch_all(
                cursor,
                """
                SELECT *
                FROM VW_AN_RESOURCE_USAGE
                ORDER BY RESOURCE_ID
                """
            )

            resource_ranking = self._fetch_all(
                cursor,
                """
                SELECT
                    RESOURCE_NAME,
                    HISTORICAL_UNITS,
                    REQUESTED_UNITS,
                    DENSE_RANK() OVER (
                        ORDER BY HISTORICAL_UNITS DESC
                    ) AS USAGE_RANK
                FROM VW_AN_RESOURCE_USAGE
                ORDER BY USAGE_RANK, RESOURCE_NAME
                """
            )

            transactions = self._fetch_one(
                cursor,
                "SELECT * FROM VW_AN_TRANSACTION_SUMMARY"
            )

            transaction_states = self._fetch_all(
                cursor,
                """
                SELECT STATUS, TOTAL
                FROM VW_AN_TRANSACTION_STATES
                ORDER BY STATUS
                """
            )

            failure_reasons = self._fetch_all(
                cursor,
                """
                SELECT
                    L.DESCRIPTION AS REASON,
                    COUNT(*) AS TOTAL
                FROM TRANSACTION_LOGS L
                JOIN TRANSACTIONS T
                  ON T.TRANSACTION_ID = L.TRANSACTION_ID
                WHERE T.TRANSACTION_STATUS = 'ROLLED_BACK'
                  AND L.EVENT_TYPE = 'ROLLBACK'
                GROUP BY L.DESCRIPTION
                ORDER BY TOTAL DESC, REASON
                """
            )

            integrity = self._fetch_one(
                cursor,
                "SELECT * FROM VW_AN_INTEGRITY"
            )

            insights = self._fetch_all(
                cursor,
                """
                SELECT CATEGORY, INSIGHT
                FROM VW_AN_SYSTEM_INSIGHTS
                ORDER BY CATEGORY
                """
            )

            recovery = self._fetch_one(
                cursor,
                """
                SELECT COUNT(*) AS RECOVERY_COUNT
                FROM DEADLOCK_RECOVERY_LOG
                """
            )

            system_logs = self._fetch_one(
                cursor,
                """
                SELECT COUNT(*) AS LOG_COUNT
                FROM SYSTEM_LOGS
                """
            )

            return {
                "success": True,
                "operations": operations,
                "processes": processes,
                "process_states": process_states,
                "departments": departments,
                "resources": resources,
                "resource_ranking": resource_ranking,
                "transactions": transactions,
                "transaction_states": transaction_states,
                "failure_reasons": failure_reasons,
                "integrity": integrity,
                "insights": insights,
                "recovery": recovery,
                "system_logs": system_logs,
                "message": "Analytics loaded from Oracle."
            }

        finally:
            cursor.close()
            connection.close()
