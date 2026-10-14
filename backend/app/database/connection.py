"""
---------------------------------------------------------
Transera Database Connection
---------------------------------------------------------
Author : Transera Team
Purpose : Connect Python Backend with Oracle Database
---------------------------------------------------------
"""

import oracledb

try:
    oracledb.init_oracle_client(
        lib_dir=r"C:\Oracle\instantclient_23_26\instantclient_23_26"
    )
except Exception:
    pass


# =====================================================
# DATABASE CONFIGURATION
# =====================================================

DB_USERNAME = "TRANSERA"
DB_PASSWORD = "transera"
DB_DSN = "localhost:1521/XE"


# =====================================================
# DATABASE CONNECTION FUNCTION
# =====================================================

def get_connection():

    try:

        connection = oracledb.connect(

            user=DB_USERNAME,
            password=DB_PASSWORD,
            dsn=DB_DSN

        )

        return connection

    except Exception as e:

        print("Database Connection Failed")
        print(e)

        return None


# =====================================================
# TEST CONNECTION
# =====================================================

if __name__ == "__main__":

    connection = get_connection()

    if connection:

        print("===================================")
        print(" Oracle Connected Successfully ")
        print("===================================")

        connection.close()

        print("Connection Closed")