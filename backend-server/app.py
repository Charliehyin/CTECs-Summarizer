from flask import Flask
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
from endpoints.retrieve_homepage_data import homepage_bp
from endpoints.retrieve_class_data import class_data_bp
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

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
app.register_blueprint(class_data_bp, url_prefix="/api")
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True, threaded=True)