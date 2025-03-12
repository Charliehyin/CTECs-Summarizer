from flask import Flask
from flask_cors import CORS
from config.config import load_config
from endpoints.chat import chat_bp
from endpoints.rag import rag_bp
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
# Update CORS to allow both localhost and your production domain
CORS(app, resources={r"/*": {"origins": ["http://localhost:3000", "https://ctecs.nu"]}})

# Load any configuration (if needed in app context)
config = load_config()

# Register the chat endpoint blueprint at the /api prefix
app.register_blueprint(chat_bp, url_prefix="/api")
app.register_blueprint(rag_bp, url_prefix="/api")

if __name__ == '__main__':
    app.run(debug=True)
