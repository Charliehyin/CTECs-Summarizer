import json
import time
from flask import Blueprint, request, jsonify
from utils.connect_db import get_db_connection

create_chat_bp = Blueprint('create_chat', __name__)

@create_chat_bp.route('/create_chat', methods=['POST'])
def create_chat():
    body = request.json
    user_id = body.get('user_id', 'guest')
    title = body.get('title', 'New Chat')
    
    # Get database connection
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Failed to connect to database"}), 500
    
    cursor = None
    try:
        cursor = conn.cursor()
        timestamp = int(time.time())
        
        # Insert new chat
        cursor.execute(
            "INSERT INTO chats (user_id) VALUES (%s)",
            (user_id,)
        )
        conn.commit()
        
        # Get the ID of the newly created chat
        chat_id = cursor.lastrowid
        
        return jsonify({'chatId': chat_id})
        
    except Exception as e:
        print(f"Error creating chat: {str(e)}")
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
