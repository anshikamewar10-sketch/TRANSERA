import oracledb

oracledb.init_oracle_client(
    lib_dir=r"C:\Oracle\instantclient_23_26\instantclient_23_26"
)

connection = oracledb.connect(
    user="TRANSERA",
    password="transera",
    dsn="localhost:1521/XE"
)

cursor = connection.cursor()

cursor.execute("""
insert into TEST_CONNECTION (ID, NAME) values (1, 'John Doe')
""")


'''rows = cursor.fetchall()
for row in rows:
    print(row)'''

connection.commit()

print("table created sucessfully")

cursor.close()
connection.close()