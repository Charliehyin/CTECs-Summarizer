from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
import time
import os
from dotenv import load_dotenv

app = Flask(__name__)
CORS(app)

load_dotenv()

def load_config():
    config = {}
    with open('assistant_config.txt', 'r') as f:
        for line in f:
            key, value = line.strip().split('=')
            config[key] = value
    return config

config = load_config()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.route('/api/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message')
    
    thread = client.beta.threads.create(
        messages=[
            {
                "role": "user",
                "content": user_message,
                "attachments": [
                    {
                        "file_id": config['MESSAGE_FILE_ID'],
                        "tools": [{"type": "file_search"}]
                    }
                ],
            }
        ]
    )
    
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=config['ASSISTANT_ID']
    )
    
    while True:
        run_status = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id
        )
        if run_status.status == 'completed':
            break
        time.sleep(2)
    
    messages = client.beta.threads.messages.list(thread_id=thread.id)
    for message in messages.data:
        if message.role == "assistant":
            return jsonify({"response": message.content[0].text.value})

if __name__ == '__main__':
    app.run(debug=True)