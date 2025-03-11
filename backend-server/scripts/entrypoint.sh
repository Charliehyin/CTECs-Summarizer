#!/bin/sh
# Run the assistant initialization script before starting the server
python scripts/init_assistant.py
# Start the Flask application
gunicorn --workers=4 --bind=0.0.0.0:5000 wsgi:app
