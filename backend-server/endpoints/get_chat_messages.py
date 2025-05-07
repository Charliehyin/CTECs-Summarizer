from flask import Blueprint, request, jsonify
from utils.connect_db import get_db_connection

get_chat_messages_bp = Blueprint('get_chat_messages', __name__)

@get_chat_messages_bp.route('/get_chat_messages', methods=['POST', 'GET'])
def get_chat_messages():
    # Handle both POST and GET methods
    if request.method == 'POST':
        chat_id = request.json.get('chatId')
    else:  # GET
        chat_id = request.args.get('chat_id')
    
    if not chat_id:
        return jsonify({"error": "Missing chat_id parameter"}), 400
    
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
                message_id, 
                message_text, 
                is_user,
                message_timestamp
            FROM messages 
            WHERE chat_id = %s 
            ORDER BY message_id ASC
            """,
            (chat_id,)
        )
        
        messages = cursor.fetchall()
        
        # Print summary stats
        user_count = sum(1 for msg in messages if msg['is_user'])
        assistant_count = sum(1 for msg in messages if not msg['is_user'])
        print(f"Retrieved {len(messages)} messages: {user_count} user, {assistant_count} assistant")
        
        # For backwards compatibility with POST method
        if request.method == 'POST':
            # Format messages according to the old format
            formatted_messages = [{
                'id': msg['message_id'],
                'text': msg['message_text'],
                'isUser': msg['is_user'],
                'timestamp': int(msg['message_timestamp'].timestamp() * 1000) if msg['message_timestamp'] else None
            } for msg in messages]
            return jsonify({'messages': formatted_messages})
        else:
            # Return messages in the new format for GET method
            return jsonify(messages)
        
    except Exception as e:
        print(f"Error retrieving messages: {str(e)}")
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
