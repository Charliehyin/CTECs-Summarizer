from flask import Flask, request, jsonify, make_response
# We're no longer using Flask-CORS
from config.config import load_config
from endpoints.chat import chat_bp
from endpoints.rag import rag_bp
from endpoints.test import test_bp
from endpoints.create_chat import create_chat_bp
from endpoints.delete_chat import delete_chat_bp
from endpoints.get_chat_history import get_chat_history_bp
from endpoints.get_chat_messages import get_chat_messages_bp
from endpoints.save_chat_message import save_chat_message_bp
from endpoints.ner import ner_bp
from endpoints.retrieve_homepage_data import homepage_bp
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Get allowed origins from environment or use default
allowed_origins = os.environ.get('ALLOWED_ORIGINS', 'http://localhost:3000,https://ctecs.nu')
origins = allowed_origins.split(',')

# Simple CORS middleware - applies to all routes
@app.before_request
def handle_preflight():
    # Handle OPTIONS requests (preflight)
    if request.method == 'OPTIONS':
        response = make_response()
        origin = request.headers.get('Origin', '')
        
        # Always allow specific origins
        if origin in origins:
            response.headers.add('Access-Control-Allow-Origin', origin)
            response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
            response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
            response.headers.add('Access-Control-Allow-Credentials', 'true')
            response.headers.add('Access-Control-Max-Age', '3600')  # Cache preflight for 1 hour
        
        return response

# Add CORS headers to all responses
@app.after_request
def add_cors_headers(response):
    origin = request.headers.get('Origin', '')
    
    # Always allow specific origins
    if origin in origins:
        response.headers['Access-Control-Allow-Origin'] = origin
        response.headers['Access-Control-Allow-Credentials'] = 'true'
    
    return response

app.config['PROPAGATE_EXCEPTIONS'] = True
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False

# Load any configuration (if needed in app context)
config = load_config()

# Register the chat endpoint blueprint at the /api prefix
app.register_blueprint(chat_bp, url_prefix="/api")
app.register_blueprint(rag_bp, url_prefix="/api")
app.register_blueprint(test_bp, url_prefix="/api")
app.register_blueprint(create_chat_bp, url_prefix="/api")
app.register_blueprint(delete_chat_bp, url_prefix="/api")
app.register_blueprint(get_chat_history_bp, url_prefix="/api")
app.register_blueprint(get_chat_messages_bp, url_prefix="/api")
app.register_blueprint(save_chat_message_bp, url_prefix="/api")
app.register_blueprint(ner_bp, url_prefix="/api")
app.register_blueprint(homepage_bp, url_prefix="/api")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True, threaded=True)
