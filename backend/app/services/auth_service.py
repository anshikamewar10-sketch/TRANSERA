"""
---------------------------------------------------------
Authentication Service
---------------------------------------------------------
Purpose:
Validates user login credentials.
---------------------------------------------------------
"""

from app.database.connection import get_connection
from app.models.auth_model import LoginRequest


class AuthService:

    def __init__(self):

        self.connection = get_connection()

    def login(self, request: LoginRequest):

        cursor = self.connection.cursor()

        cursor.execute(
            """
            SELECT
                USER_ID,
                USERNAME,
                ROLE,
                STATUS
            FROM USERS
            WHERE USERNAME = :1
            AND PASSWORD = :2
            AND STATUS = 'ACTIVE'
            """,
            (
                request.username,
                request.password
            )
        )

        user = cursor.fetchone()

        cursor.close()

        if user:

            return {

                "success": True,

                "user_id": user[0],

                "username": user[1],

                "role": user[2],

                "message": "Login Successful."

            }

        return {

            "success": False,

            "message": "Invalid Username or Password."

        }