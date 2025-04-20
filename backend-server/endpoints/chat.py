from flask import Blueprint, request, jsonify
import json
from utils.openai_client import client
from config.config import load_config

chat_bp = Blueprint('chat', __name__)
config = load_config()

with open('base_messages.json', 'r') as f:
    BASE_MESSAGES = json.load(f)

@chat_bp.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message')
    if not user_message:
        return jsonify({"error": "Missing message in request"}), 400

    try:
        messages = BASE_MESSAGES.copy()
        messages.append({"role": "user", "content": user_message})
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages
        )
        
        assistant_response = response.choices[0].message.content
        
        return jsonify({"response": assistant_response})

    except Exception as e:
        print("Error processing request:", e)
        return jsonify({"error": "Internal server error."}), 500
