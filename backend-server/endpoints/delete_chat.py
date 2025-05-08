from flask import Blueprint, request, jsonify
from utils.connect_db import get_db_connection

delete_chat_bp = Blueprint('delete_chat', __name__)

@delete_chat_bp.route('/delete_chat/<int:chat_id>', methods=['DELETE'])
def delete_chat(chat_id):
    # Handle OPTIONS preflight request
    if request.method == 'OPTIONS':
        return jsonify({})
    
    # Get database connection
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Failed to connect to database"}), 500
    
    cursor = None
    try:
        cursor = conn.cursor()
        
        # Delete messages first (due to foreign key constraints)
        cursor.execute(
            "DELETE FROM messages WHERE chat_id = %s",
            (chat_id,)
        )
        
        # Delete chat
        cursor.execute(
            "DELETE FROM chats WHERE chat_id = %s",
            (chat_id,)
        )
        
        conn.commit()
        
        return jsonify({'status': 'success', 'message': f'Chat {chat_id} deleted'})
        
    except Exception as e:
        print(f"Error deleting chat: {str(e)}")
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
