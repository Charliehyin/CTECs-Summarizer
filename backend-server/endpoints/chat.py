from flask import Blueprint, request, jsonify
import time
from utils.openai_client import client
from config.config import load_config

chat_bp = Blueprint('chat', __name__)
config = load_config()

@chat_bp.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message')
    if not user_message:
        return jsonify({"error": "Missing message in request"}), 400

    try:
        # Create a thread with the user message and file attachment for file_search
        thread = client.beta.threads.create(
            messages=[
                {
                    "role": "user",
                    "content": user_message,
                    "attachments": [
                        {
                            "file_id": config.get('MESSAGE_FILE_ID'),
                            "tools": [{"type": "file_search"}]
                        }
                    ],
                }
            ]
        )

        # Start the assistant run using the assistant ID
        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=config.get('ASSISTANT_ID')
        )

        # Poll for the response (timeout after 60 seconds)
        timeout = 60
        start_time = time.time()
        while time.time() - start_time < timeout:
            run_status = client.beta.threads.runs.retrieve(
                thread_id=thread.id,
                run_id=run.id
            )
            if run_status.status == 'completed':
                break
            time.sleep(2)
        else:
            return jsonify({"error": "Response timed out."}), 504

        # Retrieve messages from the thread and return the assistant's response
        messages = client.beta.threads.messages.list(thread_id=thread.id)
        for message in messages.data:
            if message.role == "assistant":
                return jsonify({"response": message.content[0].text.value})
        
        return jsonify({"error": "No assistant response found."}), 500

    except Exception as e:
        print("Error processing request:", e)
        return jsonify({"error": "Internal server error."}), 500
