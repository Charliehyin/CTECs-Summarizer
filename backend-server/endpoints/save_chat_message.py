import time
from flask import Blueprint, request, jsonify
from utils.connect_db import get_db_connection

save_chat_message_bp = Blueprint('save_chat_message', __name__)

@save_chat_message_bp.route('/save_chat_message', methods=['POST'])
def save_chat_message():
    try:
        body = request.json
        chat_id = body.get('chatId')
        message = body.get('message', '')
        is_user = body.get('isUser', False)
        
        # Ensure proper type for isUser
        if isinstance(is_user, str):
            is_user = is_user.lower() == 'true'
        
        # Log for debugging
        print(f"Saving message for chat: {chat_id}, isUser: {is_user}, message length: {len(message) if message else 0}")
        
        if not chat_id:
            return jsonify({"error": "Missing chatId parameter"}), 400
        
        # Ensure message is not None
        if message is None:
            message = ""
            print("Warning: Received None message, converting to empty string")
            
        # Get database connection
        conn = get_db_connection()
        if not conn:
            return jsonify({"error": "Failed to connect to database"}), 500
        
        cursor = None
        try:
            cursor = conn.cursor()
            
            # Get the next message_id for this chat
            cursor.execute(
                "SELECT COALESCE(MAX(message_id), 0) + 1 FROM messages WHERE chat_id = %s",
                (chat_id,)
            )
            message_id = cursor.fetchone()[0]
            
            # Insert message
            cursor.execute(
                """
                INSERT INTO messages 
                (chat_id, message_id, message_text, is_user, message_timestamp) 
                VALUES (%s, %s, %s, %s, FROM_UNIXTIME(%s))
                """,
                (chat_id, message_id, message, is_user, int(time.time()))
            )
            
            # Update chat's last_modified timestamp
            cursor.execute(
                "UPDATE chats SET last_modified = CURRENT_TIMESTAMP WHERE chat_id = %s",
                (chat_id,)
            )
            
            conn.commit()
            
            return jsonify({'success': True, 'messageId': message_id})
            
        except Exception as e:
            print(f"Error in save_chat_message: {str(e)}")
            conn.rollback()
            return jsonify({"error": str(e)}), 500
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
                
    except Exception as e:
        print(f"Error in save_chat_message: {str(e)}")
        return jsonify({"error": str(e)}), 500
