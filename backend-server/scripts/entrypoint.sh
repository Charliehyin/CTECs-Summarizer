#!/bin/sh
# Run the assistant initialization script before starting the server
python scripts/init_assistant.py
# Start the Flask application
exec python app.py
