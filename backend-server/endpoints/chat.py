from flask import Blueprint, request, jsonify, Response
from utils.openai_client import client
from config.config import load_config
from utils.connect_db import get_db_connection
import requests
import json
import time
import mysql.connector

chat_bp = Blueprint('chat', __name__)
config = load_config()

def ner_api(messages):
    """Call the NER API to extract entities from the messages
    If messages is a string, process as a single message
    If messages is a list, process each message and combine entities"""
    try:
        # Handle both single message (string) and multiple messages (list)
        if isinstance(messages, str):
            payload = {
                "message": messages
            }
        else:
            # Join multiple messages with newlines for processing
            combined_message = "\n".join(messages)
            payload = {
                "message": combined_message
            }

        response = requests.get(
            "http://localhost:8000/api/ner",
            json=payload
        )

        if response.status_code == 200:
            response_json = response.json()
            all_matches = response_json.get("numbers", []) + response_json.get("courses", []) + response_json.get("professors", [])
            return all_matches
        else:
            print(f"Error calling NER API: {response.status_code}")
            return {}
    except Exception as e:
        print(f"Error calling NER API: {e}")
        return {}

def rag_api(message, top_k=10, metadata=None):
    """Call the RAG API to get relevant CTECs"""
    try:
        # Prepare the request payload
        payload = {
            "message": message,
            "top_k": top_k
        }
        
        # Add metadata if provided
        if metadata:
            payload["metadata"] = metadata
            
        # Call the local rag endpoint
        response = requests.post(
            "http://localhost:8000/api/rag",
            json=payload
        )
        
        # If the request was successful, return the CTECs
        if response.status_code == 200:
            response_json = response.json()
            return response_json.get("response", "")
        else:
            print(f"Error calling RAG endpoint: {response.status_code}")
            return "Error retrieving relevant CTECs."
    except Exception as e:
        print(f"Error getting relevant CTECs: {e}")
        return "Error retrieving relevant CTECs."

@chat_bp.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message')
    if not user_message:
        return jsonify({"error": "Missing message in request"}), 400

    try:
        # Step 1: Call NER API to extract entities
        ner_response = ner_api(user_message)
        
        # Step 2: Call RAG API with user message and NER metadata
        rag_response = rag_api(user_message, top_k=10, metadata=ner_response)
        
        # Step 3: Combine user message with RAG context
        augmented_message = f"{user_message}\n\nHere is the context to use for the response: {rag_response}"
        
        system_message = """You are analyzing student reviews of courses at Northwestern. 
        Use the provided CTEC (Course and Teacher Evaluation Council) data to answer questions about these course reviews.
        Base your responses only on the CTEC content provided in the conversation."""
        
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": augmented_message}
        ]
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages
        )
        
        assistant_response = response.choices[0].message.content
        
        return jsonify({"response": assistant_response})

    except Exception as e:
        print("Error processing request:", e)
        return jsonify({"error": "Internal server error."}), 500

@chat_bp.route('/chat-stream', methods=['POST'])
def chat_stream():
    data = request.json
    message = data['message']
    chat_id = data.get('chatId')
    user_id = data.get('user_id', 'guest')
    
    # Get a MySQL connection
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Failed to connect to database"}), 500
    
    cursor = None
    
    try:
        cursor = conn.cursor(dictionary=True)
        
        # If no chat_id provided, create a new chat
        if not chat_id:
            # Create a new chat
            cursor.execute(
                "INSERT INTO chats (user_id) VALUES (%s)",
                (user_id,)
            )
            conn.commit()
            chat_id = cursor.lastrowid
            
        # Get the current max message_id
        cursor.execute(
            "SELECT COALESCE(MAX(message_id), 0) FROM messages WHERE chat_id = %s",
            (chat_id,)
        )
        result = cursor.fetchone()
        current_max_id = result['COALESCE(MAX(message_id), 0)'] if result else 0
        
        # Fetch chat history for this chat
        cursor.execute(
            "SELECT message_id, message_text, is_user FROM messages WHERE chat_id = %s ORDER BY message_id",
            (chat_id,)
        )
        chat_history = cursor.fetchall()
        
        # Get the last 10 user messages for NER
        user_messages = [msg['message_text'] for msg in chat_history if msg['is_user']]
        recent_user_messages = user_messages[-10:] if user_messages else []
        # Add current message
        recent_user_messages.append(message)
        
        # Save current user message to database
        user_timestamp = int(time.time())
        next_message_id = current_max_id + 1
        
        cursor.execute(
            "INSERT INTO messages (chat_id, message_id, message_text, is_user, message_timestamp) VALUES (%s, %s, %s, %s, FROM_UNIXTIME(%s))",
            (chat_id, next_message_id, message, True, user_timestamp)
        )
        
        cursor.execute(
            "UPDATE chats SET last_modified = FROM_UNIXTIME(%s) WHERE chat_id = %s",
            (user_timestamp, chat_id)
        )
        
        conn.commit()
        
        # Re-fetch to get updated chat history including the new message
        cursor.execute(
            "SELECT message_id, message_text, is_user FROM messages WHERE chat_id = %s ORDER BY message_id",
            (chat_id,)
        )
        updated_chat_history = cursor.fetchall()
        
        # Close connection before streaming (generator will create its own)
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        
        def generate():
            full_content = ""  # store the complete response
            
            try:
                # Step 1: Call NER API with the last 10 user messages
                ner_response = ner_api(recent_user_messages)
                
                # Step 2: Call RAG API with current user message only and NER metadata
                rag_response = rag_api(message, top_k=10, metadata=ner_response)
                
                # Step 3: Prepare the full chat history for OpenAI
                api_messages = [
                    {"role": "system", "content": """You are analyzing student reviews of courses at Northwestern. 
                    Use the provided CTEC (Course and Teacher Evaluation Council) data to answer questions about these course reviews.
                    Base your responses only on the CTEC content provided in the conversation."""}
                ]
                
                # Add chat history
                for msg in updated_chat_history:
                    if msg['is_user']:
                        api_messages.append({"role": "user", "content": msg['message_text']})
                    else:
                        api_messages.append({"role": "assistant", "content": msg['message_text']})
                
                # Append the RAG context to the last user message
                if api_messages[-1]['role'] == 'user':
                    api_messages[-1]['content'] += f"\n\nHere is the context to use for the response: {rag_response}"
                
                # Call OpenAI API with streaming enabled
                try:
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=api_messages,
                        stream=True,
                        temperature=0.7,
                    )
                    
                    # Process the streaming response
                    for chunk in response:
                        if chunk.choices and len(chunk.choices) > 0:
                            delta = chunk.choices[0].delta
                            
                            # If there's content in this chunk
                            if hasattr(delta, 'content') and delta.content:
                                content = delta.content
                                full_content += content  # Accumulate the content
                                
                                # Stream the chunk to the client
                                chunk_data = f"data: {json.dumps({'chunk': content})}\n\n"
                                yield chunk_data
                    
                    # Send the full content at the end as a 'done' message
                    yield f"data: {json.dumps({'done': True, 'complete': full_content})}\n\n"
                    
                    # Save the assistant's message to the database
                    assistant_timestamp = int(time.time())
                    next_message_id = current_max_id + 2  # +1 for user message, +1 for assistant
                    
                    # Get a new connection for the assistant message since we're in a generator
                    asst_conn = get_db_connection()
                    if asst_conn:
                        try:
                            asst_cursor = asst_conn.cursor()
                            # Insert assistant message
                            asst_cursor.execute(
                                "INSERT INTO messages (chat_id, message_id, message_text, is_user, message_timestamp) VALUES (%s, %s, %s, %s, FROM_UNIXTIME(%s))",
                                (chat_id, next_message_id, full_content, False, assistant_timestamp)
                            )
                            
                            # Update chat's last_modified timestamp
                            asst_cursor.execute(
                                "UPDATE chats SET last_modified = FROM_UNIXTIME(%s) WHERE chat_id = %s",
                                (assistant_timestamp, chat_id)
                            )
                            asst_conn.commit()
                            asst_cursor.close()
                        except Exception as e:
                            print(f"Error saving assistant message: {e}")
                        finally:
                            asst_conn.close()
                    
                except Exception as e:
                    print(f"Error in streaming response: {e}")
                    yield f"data: {json.dumps({'chunk': 'I could not generate a response. Please try again.'})}\n\n"
                    yield f"data: {json.dumps({'done': True})}\n\n"
                    
            except Exception as e:
                print(f"Error in generate function: {e}")
                yield f"data: {json.dumps({'chunk': 'I could not generate a response. Please try again.'})}\n\n"
                yield f"data: {json.dumps({'done': True})}\n\n"
        
        return Response(generate(), mimetype='text/event-stream')
        
    except Exception as e:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        print(f"Error in chat_stream: {e}")
        return jsonify({"error": str(e)}), 500