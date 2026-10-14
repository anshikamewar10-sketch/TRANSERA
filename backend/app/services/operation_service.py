"""
---------------------------------------------------------
Operation Service
---------------------------------------------------------
Purpose:
Handles all Business Operation related database operations.
---------------------------------------------------------
"""

from app.database.connection import get_connection
from app.models.operation_model import OperationCreate


class OperationService:

    def __init__(self):
        self.connection = get_connection()

    # --------------------------------------------------
    # CREATE OPERATION
    # --------------------------------------------------

    def create_operation(self, operation: OperationCreate):

        cursor = self.connection.cursor()

        cursor.execute("""
            SELECT NVL(MAX(TO_NUMBER(SUBSTR(OPERATION_ID,3))),0)+1
            FROM BUSINESS_OPERATIONS
        """)

        next_id = cursor.fetchone()[0]

        operation_id = f"OP{next_id:03d}"

        query = """
        INSERT INTO BUSINESS_OPERATIONS
        (
            OPERATION_ID,
            USER_ID,
            PRODUCT_ID,
            OPERATION_TYPE,
            DESCRIPTION,
            DEPARTMENT,
            OPERATION_QUANTITY,
            OPERATION_MODE,
            PRIORITY,
            BUSINESS_STATUS,
            CREATED_AT
        )
        VALUES
        (
            :1,:2,:3,:4,:5,:6,:7,:8,:9,
            'PENDING',
            CURRENT_TIMESTAMP
        )
        """

        cursor.execute(
            query,
            (
                operation_id,
                operation.user_id,
                operation.product_id,
                operation.operation_type,
                operation.description,
                operation.department,
                operation.operation_quantity,
                operation.operation_mode,
                operation.priority
            )
        )

        self.connection.commit()

        cursor.close()

        return {
            "success": True,
            "operation_id": operation_id,
            "message": "Operation created successfully."
        }

    # --------------------------------------------------
    # VIEW ALL OPERATIONS
    # --------------------------------------------------

    def get_all_operations(self):

        cursor = self.connection.cursor()

        query = """
        SELECT
            OPERATION_ID,
            USER_ID,
            PRODUCT_ID,
            OPERATION_TYPE,
            DESCRIPTION,
            DEPARTMENT,
            OPERATION_QUANTITY,
            OPERATION_MODE,
            PRIORITY,
            BUSINESS_STATUS,
            CREATED_AT
        FROM BUSINESS_OPERATIONS
        ORDER BY CREATED_AT DESC
        """

        cursor.execute(query)

        rows = cursor.fetchall()

        operations = []

        for row in rows:

            operations.append({
                "operation_id": row[0],
                "user_id": row[1],
                "product_id": row[2],
                "operation_type": row[3],
                "description": row[4],
                "department": row[5],
                "operation_quantity": row[6],
                "operation_mode": row[7],
                "priority": row[8],
                "business_status": row[9],
                "created_at": str(row[10])
            })

        cursor.close()

        return {
            "success": True,
            "count": len(operations),
            "operations": operations
        }

    # --------------------------------------------------
    # SEARCH OPERATION
    # --------------------------------------------------

    def search_operation(self, keyword):

        cursor = self.connection.cursor()

        query = """
        SELECT
            OPERATION_ID,
            OPERATION_TYPE,
            DEPARTMENT,
            BUSINESS_STATUS
        FROM BUSINESS_OPERATIONS
        WHERE
            UPPER(OPERATION_TYPE) LIKE UPPER(:1)
            OR UPPER(DEPARTMENT) LIKE UPPER(:2)
        """

        cursor.execute(
            query,
            (
                f"%{keyword}%",
                f"%{keyword}%"
            )
        )

        rows = cursor.fetchall()

        cursor.close()

        return rows

    # --------------------------------------------------
    # UPDATE STATUS
    # --------------------------------------------------

    def update_status(self, operation_id, status):

        cursor = self.connection.cursor()

        cursor.execute(
            """
            UPDATE BUSINESS_OPERATIONS
            SET BUSINESS_STATUS=:1
            WHERE OPERATION_ID=:2
            """,
            (
                status,
                operation_id
            )
        )

        self.connection.commit()

        cursor.close()

        return {
            "success": True,
            "message": "Status Updated Successfully."
        }
            # =====================================================
    # GET OPERATION DETAILS
    # =====================================================

    def get_operation_details(self, operation_id):

        cursor = self.connection.cursor()

        cursor.execute(
            """
            SELECT
                OPERATION_ID,
                USER_ID,
                PRODUCT_ID,
                OPERATION_TYPE,
                DESCRIPTION,
                DEPARTMENT,
                OPERATION_QUANTITY,
                OPERATION_MODE,
                PRIORITY,
                BUSINESS_STATUS,
                CREATED_AT
            FROM BUSINESS_OPERATIONS
            WHERE OPERATION_ID = :1
            """,
            (
                operation_id,
            )
        )

        row = cursor.fetchone()

        cursor.close()

        if row is None:

            return {

                "success": False,

                "message": "Operation Not Found."

            }

        return {

            "success": True,

            "operation": {

                "operation_id": row[0],

                "user_id": row[1],

                "product_id": row[2],

                "operation_type": row[3],

                "description": row[4],

                "department": row[5],

                "operation_quantity": row[6],

                "operation_mode": row[7],

                "priority": row[8],

                "business_status": row[9],

                "created_at": row[10].strftime("%Y-%m-%d %H:%M:%S")

            }

        }