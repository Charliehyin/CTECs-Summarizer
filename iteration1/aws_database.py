import mysql.connector  # Use psycopg2 for PostgreSQL

# AWS RDS connection details
db_config = {
    "host": "ctecdb.cl6gmcm2s7td.us-east-2.rds.amazonaws.com", 
    "user": "admin",  # Your RDS username
    "password": "ctecparser123",  # Your RDS password
    "database": "ctecdb",  # Your database name
    "port": 3306  # Default MySQL port (5432 for PostgreSQL)
}

def get_db_connection():
    """Connect to AWS RDS and return the connection object."""
    try:
        conn = mysql.connector.connect(**db_config)
        print("Connected to AWS RDS successfully!")
        return conn
    except mysql.connector.Error as err:
        print(f"Error connecting to RDS: {err}")
        return None
