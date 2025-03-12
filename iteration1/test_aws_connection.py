from aws_database import get_db_connection

connection = get_db_connection()

if connection:
    print("Successfully connected to AWS RDS.")
    connection.close()
else:
    print("Connection failed.")