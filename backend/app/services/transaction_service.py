
"""
TRANSERA - Transaction Center
Oracle DBMS transaction processing.
"""

from app.database.connection import get_connection


class TransactionService:

    SUPPORTED_TYPES = (
        "Inventory Receipt",
        "Sales Order",
        "Inventory Audit"
    )

    def _next_id(self, cursor, table, column, prefix):
        cursor.execute(f"""
            SELECT NVL(MAX(
                CASE
                    WHEN REGEXP_LIKE(
                        {column}, '^{prefix}[0-9]+$'
                    )
                    THEN TO_NUMBER(SUBSTR({column}, 3))
                END
            ), 0) + 1
            FROM {table}
        """)
        return f"{prefix}{int(cursor.fetchone()[0]):03d}"

    def _insert_log(
        self, cursor, transaction_id,
        event_type, table_name, description
    ):
        log_id = self._next_id(
            cursor, "TRANSACTION_LOGS", "LOG_ID", "TL"
        )

        cursor.execute("""
            INSERT INTO TRANSACTION_LOGS
            (
                LOG_ID, TRANSACTION_ID, EVENT_TYPE,
                TABLE_NAME, DESCRIPTION, LOG_TIME
            )
            VALUES (
                :1, :2, :3, :4, :5, CURRENT_TIMESTAMP
            )
        """, (
            log_id,
            transaction_id,
            event_type,
            table_name,
            str(description)[:100]
        ))

    def _record_failure(
        self, connection, process_id,
        operation_id, reason
    ):
        cursor = connection.cursor()

        try:
            transaction_id = self._next_id(
                cursor, "TRANSACTIONS",
                "TRANSACTION_ID", "TX"
            )

            cursor.execute("""
                INSERT INTO TRANSACTIONS
                (
                    TRANSACTION_ID, PROCESS_ID,
                    OPERATION_ID, TRANSACTION_STATUS,
                    START_TIME, END_TIME
                )
                VALUES (
                    :1, :2, :3, 'ROLLED_BACK',
                    CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
                )
            """, (
                transaction_id,
                process_id,
                operation_id
            ))

            self._insert_log(
                cursor, transaction_id,
                "ROLLBACK", "INVENTORY", reason
            )

            connection.commit()
            return transaction_id

        except Exception:
            connection.rollback()
            raise

        finally:
            cursor.close()

    def execute_one(self, process_id, operation_id):
        connection = get_connection()
        cursor = connection.cursor()

        try:
            # Lock the business operation to prevent
            # concurrent duplicate execution.
            cursor.execute("""
                SELECT
                    B.OPERATION_TYPE,
                    B.PRODUCT_ID,
                    B.OPERATION_QUANTITY,
                    B.BUSINESS_STATUS,
                    P.PROCESS_STATE
                FROM BUSINESS_OPERATIONS B
                JOIN PROCESSES P
                    ON B.OPERATION_ID = P.OPERATION_ID
                WHERE B.OPERATION_ID = :1
                  AND P.PROCESS_ID = :2
                FOR UPDATE OF B.BUSINESS_STATUS
            """, (operation_id, process_id))

            row = cursor.fetchone()

            if not row:
                connection.rollback()
                return {
                    "operation_id": operation_id,
                    "status": "ERROR",
                    "message": "Operation or process not found."
                }

            operation_type, product_id, quantity, \
                business_status, process_state = row

            if (
                business_status != "COMPLETED"
                or process_state != "TERMINATED"
            ):
                connection.rollback()
                return {
                    "operation_id": operation_id,
                    "status": "SKIPPED",
                    "message": "OS lifecycle not completed."
                }

            # Prevent duplicate transaction execution.
            cursor.execute("""
                SELECT TRANSACTION_ID, TRANSACTION_STATUS
                FROM TRANSACTIONS
                WHERE OPERATION_ID = :1
                ORDER BY START_TIME DESC, TRANSACTION_ID DESC
            """, (operation_id,))

            existing = cursor.fetchone()

            if existing:
                connection.rollback()
                return {
                    "operation_id": operation_id,
                    "transaction_id": existing[0],
                    "status": "SKIPPED",
                    "previous_status": existing[1],
                    "message": "Transaction already processed."
                }

            if operation_type not in self.SUPPORTED_TYPES:
                connection.rollback()
                return {
                    "operation_id": operation_id,
                    "status": "SKIPPED",
                    "message": "Unsupported transaction type."
                }

            transaction_id = self._next_id(
                cursor, "TRANSACTIONS",
                "TRANSACTION_ID", "TX"
            )

            cursor.execute("""
                INSERT INTO TRANSACTIONS
                (
                    TRANSACTION_ID, PROCESS_ID,
                    OPERATION_ID, TRANSACTION_STATUS,
                    START_TIME
                )
                VALUES (
                    :1, :2, :3, 'ACTIVE',
                    CURRENT_TIMESTAMP
                )
            """, (
                transaction_id,
                process_id,
                operation_id
            ))

            # Lock inventory row while processing.
            cursor.execute("""
                SELECT PRODUCT_NAME, QUANTITY
                FROM INVENTORY
                WHERE PRODUCT_ID = :1
                FOR UPDATE
            """, (product_id,))

            inventory = cursor.fetchone()

            if not inventory:
                raise ValueError("Product not found in inventory.")

            product_name = inventory[0]
            before = int(inventory[1])
            quantity = int(quantity)

            if quantity <= 0:
                raise ValueError("Operation quantity must be positive.")

            after = before

            if operation_type == "Inventory Receipt":
                after = before + quantity

                cursor.execute("""
                    UPDATE INVENTORY
                    SET QUANTITY = :1,
                        UPDATED_AT = CURRENT_TIMESTAMP
                    WHERE PRODUCT_ID = :2
                """, (after, product_id))

            elif operation_type == "Sales Order":
                if before < quantity:
                    raise ValueError(
                        f"Insufficient stock: required {quantity}, "
                        f"available {before}."
                    )

                after = before - quantity

                cursor.execute("""
                    UPDATE INVENTORY
                    SET QUANTITY = :1,
                        UPDATED_AT = CURRENT_TIMESTAMP
                    WHERE PRODUCT_ID = :2
                """, (after, product_id))

            elif operation_type == "Inventory Audit":
                after = before

            cursor.execute("""
                UPDATE TRANSACTIONS
                SET TRANSACTION_STATUS = 'COMMITTED',
                    END_TIME = CURRENT_TIMESTAMP
                WHERE TRANSACTION_ID = :1
            """, (transaction_id,))

            description = (
                f"{operation_type}: {before} to {after} units"
            )

            self._insert_log(
                cursor, transaction_id,
                "COMMIT", "INVENTORY", description
            )

            connection.commit()

            return {
                "operation_id": operation_id,
                "process_id": process_id,
                "transaction_id": transaction_id,
                "operation_type": operation_type,
                "product_id": product_id,
                "product_name": product_name,
                "quantity": quantity,
                "before_quantity": before,
                "after_quantity": after,
                "status": "COMMITTED",
                "message": "Transaction committed successfully."
            }

        except ValueError as error:
            connection.rollback()

            try:
                failed_id = self._record_failure(
                    connection, process_id,
                    operation_id, str(error)
                )
            except Exception as log_error:
                return {
                    "operation_id": operation_id,
                    "status": "ERROR",
                    "message": (
                        f"Transaction rolled back: {error}. "
                        f"Failure log could not be saved: {log_error}"
                    )
                }

            return {
                "operation_id": operation_id,
                "process_id": process_id,
                "transaction_id": failed_id,
                "status": "ROLLED_BACK",
                "message": str(error)
            }

        except Exception:
            connection.rollback()
            raise

        finally:
            cursor.close()
            connection.close()

    def execute_transactions(self):
        connection = get_connection()
        cursor = connection.cursor()

        try:
            cursor.execute("""
                SELECT P.PROCESS_ID, B.OPERATION_ID
                FROM BUSINESS_OPERATIONS B
                JOIN PROCESSES P
                    ON P.OPERATION_ID = B.OPERATION_ID
                WHERE B.BUSINESS_STATUS = 'COMPLETED'
                  AND P.PROCESS_STATE = 'TERMINATED'
                  AND B.OPERATION_TYPE IN (
                      'Inventory Receipt',
                      'Sales Order',
                      'Inventory Audit'
                  )
                  AND NOT EXISTS (
                      SELECT 1
                      FROM TRANSACTIONS T
                      WHERE T.OPERATION_ID = B.OPERATION_ID
                  )
                ORDER BY B.CREATED_AT, B.OPERATION_ID
            """)

            operations = cursor.fetchall()

        finally:
            cursor.close()
            connection.close()

        results = []

        for process_id, operation_id in operations:
            try:
                result = self.execute_one(
                    process_id, operation_id
                )
            except Exception as error:
                result = {
                    "operation_id": operation_id,
                    "process_id": process_id,
                    "status": "ERROR",
                    "message": str(error)
                }

            results.append(result)

        committed = sum(
            1 for r in results if r["status"] == "COMMITTED"
        )
        rolled_back = sum(
            1 for r in results if r["status"] == "ROLLED_BACK"
        )
        skipped = sum(
            1 for r in results if r["status"] == "SKIPPED"
        )
        errors = sum(
            1 for r in results if r["status"] == "ERROR"
        )

        return {
            "success": errors == 0,
            "total_processed": len(results),
            "committed": committed,
            "rolled_back": rolled_back,
            "skipped": skipped,
            "errors": errors,
            "results": results,
            "message": (
                "No new eligible transactions."
                if not operations
                else "Transaction batch processing completed."
            )
        }

    def get_history(self):
        connection = get_connection()
        cursor = connection.cursor()

        try:
            cursor.execute("""
                SELECT
                    T.TRANSACTION_ID,
                    T.PROCESS_ID,
                    T.OPERATION_ID,
                    B.OPERATION_TYPE,
                    B.PRODUCT_ID,
                    B.OPERATION_QUANTITY,
                    T.TRANSACTION_STATUS,
                    T.START_TIME,
                    T.END_TIME
                FROM TRANSACTIONS T
                JOIN BUSINESS_OPERATIONS B
                    ON T.OPERATION_ID = B.OPERATION_ID
                ORDER BY T.START_TIME DESC,
                         T.TRANSACTION_ID DESC
            """)

            history = []

            for row in cursor.fetchall():
                history.append({
                    "transaction_id": row[0],
                    "process_id": row[1],
                    "operation_id": row[2],
                    "operation_type": row[3],
                    "product_id": row[4],
                    "quantity": int(row[5]),
                    "status": row[6],
                    "start_time": (
                        row[7].isoformat() if row[7] else None
                    ),
                    "end_time": (
                        row[8].isoformat() if row[8] else None
                    )
                })

            cursor.execute("""
                SELECT
                    L.LOG_ID,
                    L.TRANSACTION_ID,
                    L.EVENT_TYPE,
                    L.TABLE_NAME,
                    L.DESCRIPTION,
                    L.LOG_TIME
                FROM TRANSACTION_LOGS L
                ORDER BY L.LOG_TIME DESC, L.LOG_ID DESC
            """)

            logs = []

            for row in cursor.fetchall():
                logs.append({
                    "log_id": row[0],
                    "transaction_id": row[1],
                    "event_type": row[2],
                    "table_name": row[3],
                    "description": row[4],
                    "log_time": (
                        row[5].isoformat() if row[5] else None
                    )
                })

            return {
                "success": True,
                "history": history,
                "logs": logs,
                "total": len(history),
                "committed": sum(
                    1 for t in history
                    if t["status"] == "COMMITTED"
                ),
                "rolled_back": sum(
                    1 for t in history
                    if t["status"] == "ROLLED_BACK"
                )
            }

        finally:
            cursor.close()
            connection.close()
