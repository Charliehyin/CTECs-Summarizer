from flask import Blueprint, request, jsonify
from utils.connect_db import get_db_connection

get_chat_messages_bp = Blueprint('get_chat_messages', __name__)

@get_chat_messages_bp.route('/get_chat_messages', methods=['POST'])
def get_chat_messages():
    chat_id = request.json.get('chatId')
    
    if not chat_id:
        return jsonify({"error": "Missing chatId parameter"}), 400
    
    print(f"Fetching messages for chat ID: {chat_id}")
    
    # Get database connection
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Failed to connect to database"}), 500
    
    cursor = None
    try:
        cursor = conn.cursor(dictionary=True)  # Return results as dictionaries
        
        # Get all messages for the chat
        cursor.execute(
            """
            SELECT 
                message_id as id, 
                message_text as text, 
                is_user as isUser,
                UNIX_TIMESTAMP(message_timestamp) * 1000 as timestamp
            FROM messages 
            WHERE chat_id = %s 
            ORDER BY message_id ASC
            """,
            (chat_id,)
        )
        
        messages = cursor.fetchall()
        
        # Print summary stats
        user_count = sum(1 for msg in messages if msg['isUser'])
        assistant_count = sum(1 for msg in messages if not msg['isUser'])
        print(f"Retrieved {len(messages)} messages: {user_count} user, {assistant_count} assistant")
        
        return jsonify({'messages': messages})
        
    except Exception as e:
        print(f"Error retrieving messages: {str(e)}")
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
