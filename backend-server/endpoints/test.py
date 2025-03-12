from flask import Blueprint, request, jsonify
from config.config import load_config

test_bp = Blueprint('test', __name__)
config = load_config()

# If using Flask
@test_bp.route('/test', methods=['GET'])
def test():
    response = jsonify({"status": "ok"})
    return response