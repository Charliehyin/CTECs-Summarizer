import json
import time
from flask import Blueprint, request, jsonify
from utils.connect_db import get_db_connection

create_chat_bp = Blueprint('create_chat', __name__)

@create_chat_bp.route('/create_chat', methods=['POST'])
def create_chat():
    print("Received create_chat request")
    
    body = request.json
    if body is None:
        print("Error: No JSON body in request")
        return jsonify({"error": "No JSON body in request"}), 400
    
    user_id = body.get('user_id', 'guest')
    title = body.get('title', 'New Chat')
    
    print(f"Creating new chat for user: {user_id}, title: {title}")
    
    # Get database connection
    conn = get_db_connection()
    if not conn:
        print("Error: Failed to connect to database")
        return jsonify({"error": "Failed to connect to database"}), 500
    
    cursor = None
    try:
        cursor = conn.cursor()
        timestamp = int(time.time())
        
        # Insert new chat with title
        insert_query = "INSERT INTO chats (user_id, title, last_modified) VALUES (%s, %s, FROM_UNIXTIME(%s))"
        print(f"Executing query: {insert_query} with params: ({user_id}, {title}, {timestamp})")
        
        cursor.execute(
            insert_query,
            (user_id, title, timestamp)
        )
        conn.commit()
        
        # Get the ID of the newly created chat
        chat_id = cursor.lastrowid
        print(f"Created chat with ID: {chat_id}")
        
        return jsonify({'chatId': chat_id})
        
    except Exception as e:
        error_msg = f"Error creating chat: {str(e)}"
        print(error_msg)
        if conn:
            conn.rollback()
        return jsonify({"error": error_msg}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
