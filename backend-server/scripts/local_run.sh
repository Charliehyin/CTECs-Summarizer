#!/bin/sh
# Run the assistant initialization script before starting the server
python scripts/init_assistant.py
python scripts/compute_embeddings.py

# Start the Flask application 
export FLASK_APP=app.py
flask run --host=0.0.0.0 --port=8000
