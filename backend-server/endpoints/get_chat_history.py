from flask import Blueprint, request, jsonify
from utils.connect_db import get_db_connection

get_chat_history_bp = Blueprint('get_chat_history', __name__)

@get_chat_history_bp.route('/get_chat_history', methods=['POST'])
def get_chat_history():
    user_id = request.json.get('user_id', 'guest')
    
    # Get database connection
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Failed to connect to database"}), 500
    
    cursor = None
    try:
        cursor = conn.cursor(dictionary=True)  # Return results as dictionaries
        
        # Get all chats for the user
        cursor.execute(
            "SELECT chat_id as id, user_id, last_modified as updatedAt FROM chats WHERE user_id = %s ORDER BY last_modified DESC",
            (user_id,)
        )
        
        chats = cursor.fetchall()
        
        # Format dates for JSON serialization
        for chat in chats:
            if 'updatedAt' in chat and chat['updatedAt']:
                chat['updatedAt'] = chat['updatedAt'].isoformat()
        
        return jsonify({'chats': chats})
        
    except Exception as e:
        print(f"Error getting chat history: {str(e)}")
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
