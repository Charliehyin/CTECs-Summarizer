from flask import Flask, request
from flask_cors import CORS
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
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Get allowed origins from environment or use default
allowed_origins = os.environ.get('ALLOWED_ORIGINS', 'http://localhost:3000,https://ctecs.nu')
origins = allowed_origins.split(',')

# Configure CORS with specific origins
CORS(app, 
     resources={r"/api/*": {"origins": origins}},
     supports_credentials=True)

# Add a global CORS handler to ensure consistent headers
@app.after_request
def after_request(response):
    origin = request.headers.get('Origin')
    
    # Only set CORS headers if the request has an Origin header
    if origin:
        # Check if the origin is in our allowed list
        if origin in origins:
            # Important: Remove any existing Access-Control-Allow-Origin headers
            # to avoid duplicates
            if 'Access-Control-Allow-Origin' in response.headers:
                del response.headers['Access-Control-Allow-Origin']
            
            # Set a single Access-Control-Allow-Origin header
            response.headers.add('Access-Control-Allow-Origin', origin)
        
        # Ensure other CORS headers are set consistently
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
    
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True, threaded=True)
