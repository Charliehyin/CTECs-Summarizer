import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.connect_db import get_db_connection

def check_db_schema():
    # Get database connection
    conn = get_db_connection()
    if not conn:
        print("Failed to connect to database")
        return False
    
    cursor = None
    try:
        cursor = conn.cursor()
        
        # Check tables
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        print("Tables in database:")
        for table in tables:
            print(f"  - {table[0]}")
        
        # Check chats table structure
        print("\nChats table structure:")
        cursor.execute("DESCRIBE chats")
        columns = cursor.fetchall()
        for column in columns:
            print(f"  - {column[0]}: {column[1]}, Null: {column[2]}, Key: {column[3]}, Default: {column[4]}")
        
        # Check messages table structure
        print("\nMessages table structure:")
        cursor.execute("DESCRIBE messages")
        columns = cursor.fetchall()
        for column in columns:
            print(f"  - {column[0]}: {column[1]}, Null: {column[2]}, Key: {column[3]}, Default: {column[4]}")
        
        # Check for any chats in the database
        cursor.execute("SELECT COUNT(*) FROM chats")
        chat_count = cursor.fetchone()[0]
        print(f"\nTotal chats in database: {chat_count}")
        
        if chat_count > 0:
            # Get sample chats
            cursor.execute("SELECT * FROM chats LIMIT 5")
            chats = cursor.fetchall()
            print("\nSample chats:")
            for chat in chats:
                print(f"  - Chat ID: {chat[0]}, User: {chat[1]}, Title: {chat[2] if len(chat) > 2 else 'N/A'}")
        
        return True
        
    except Exception as e:
        print(f"Error checking database: {str(e)}")
        return False
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    check_db_schema() 