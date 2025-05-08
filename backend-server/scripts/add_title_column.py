import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.connect_db import get_db_connection

def add_title_column():
    # Get database connection
    conn = get_db_connection()
    if not conn:
        print("Failed to connect to database")
        return False
    
    cursor = None
    try:
        cursor = conn.cursor()
        
        # Check if title column exists
        cursor.execute("SHOW COLUMNS FROM chats LIKE 'title'")
        if cursor.fetchone():
            print("Title column already exists in chats table")
            return True
        
        # Add title column
        cursor.execute(
            "ALTER TABLE chats ADD COLUMN title VARCHAR(255) DEFAULT 'New Chat'"
        )
        conn.commit()
        
        print("Added title column to chats table")
        return True
        
    except Exception as e:
        print(f"Error adding title column: {str(e)}")
        return False
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    add_title_column() 