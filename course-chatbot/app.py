from flask import Flask, request, jsonify, Response, stream_with_context
from flask_cors import CORS
import openai
import os
import json
from dotenv import load_dotenv
import re

app = Flask(__name__)

CORS(app, resources={
    r"/*": {
        "origins": "*",
        "methods": ["POST", "OPTIONS", "GET"],
        "allow_headers": ["Content-Type", "Accept"]
    }
})

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

print("API Key loaded:", "Yes" if openai.api_key else "No")
print("API Key length:", len(openai.api_key) if openai.api_key else 0)

with open('base_messages.json', 'r') as f:
    BASE_MESSAGES = json.load(f)

@app.route('/rag', methods=['POST'])
def rag():
    try:
        user_message = request.json.get('message')
        return jsonify({"response": ""})
    except Exception as e:
        print(f"RAG Error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/chat', methods=['POST'])
def chat():
    try:
        user_message = request.json.get('message')
        print(f"Received message: {user_message}")
        
        messages = BASE_MESSAGES.copy() + [{"role": "user", "content": user_message}]
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=messages
            )
            
            assistant_response = response.choices[0].message['content']
            
            chunk_size = 5 
            chunks = [assistant_response[i:i+chunk_size] for i in range(0, len(assistant_response), chunk_size)]
            
            def generate():
                for chunk in chunks:
                    import time
                    time.sleep(0.05)  # 50ms delay between chunks
                    yield f"data: {json.dumps({'chunk': chunk})}\n\n"
                
                yield f"data: {json.dumps({'done': True})}\n\n"
            
            return Response(stream_with_context(generate()), 
                            content_type='text/event-stream')
            
        except Exception as e:
            print("OpenAI API Error:", str(e))
            return jsonify({"error": "Error calling OpenAI API"}), 500
            
    except Exception as e:
        print(f"Chat Error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/chat-stream')
def chat_stream():
    try:
        user_message = request.args.get('message')
        print(f"Received message via SSE: {user_message}")
        
        messages = BASE_MESSAGES.copy() + [{"role": "user", "content": user_message}]
        
        def generate():
            response = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=messages,
                stream=True 
            )
            
            for chunk in response:
                if 'choices' in chunk and len(chunk['choices']) > 0:
                    delta = chunk['choices'][0].get('delta', {})
                    if 'content' in delta:
                        content = delta.get('content', '')
                        if content:
                            yield f"data: {json.dumps({'chunk': content})}\n\n"
            
            yield f"data: {json.dumps({'done': True})}\n\n"
            
        return Response(
            stream_with_context(generate()),
            content_type='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'X-Accel-Buffering': 'no'
            }
        )
        
    except Exception as e:
        print(f"Chat Error: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)