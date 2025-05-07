import mysql.connector  # Use psycopg2 for PostgreSQL
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# AWS RDS connection details
db_config = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "port": int(os.getenv("DB_PORT", "3306")),  # Default to 3306 if not specified
    "connect_timeout": 10  # Add timeout to avoid hanging
}

def get_db_connection():
    """Connect to AWS RDS and return the connection object."""
    try:
        conn = mysql.connector.connect(**db_config)
        return conn
    except mysql.connector.Error as err:
        print(f"Error connecting to RDS: {err}")
        return None