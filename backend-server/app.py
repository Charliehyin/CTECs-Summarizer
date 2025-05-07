from flask import Flask, request
# We're no longer using Flask-CORS as it's causing duplicate headers
# from flask_cors import CORS
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

# We're no longer using Flask-CORS
# CORS(app, 
#      resources={r"/api/*": {"origins": origins}},
#      supports_credentials=True)

# Instead, we're handling CORS manually with our own middleware
@app.after_request
def add_cors_headers(response):
    origin = request.headers.get('Origin')
    
    # Only add CORS headers if the request has an Origin header
    if origin:
        # Check if the origin is in our allowed list
        if origin in origins:
            response.headers['Access-Control-Allow-Origin'] = origin
            response.headers['Access-Control-Allow-Credentials'] = 'true'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    
    return response

# Handle OPTIONS requests explicitly
@app.route('/api/<path:path>', methods=['OPTIONS'])
def options_handler(path):
    response = app.make_default_options_response()
    origin = request.headers.get('Origin')
    if origin and origin in origins:
        response.headers['Access-Control-Allow-Origin'] = origin
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
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
