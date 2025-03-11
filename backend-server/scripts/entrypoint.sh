#!/bin/sh
# Run the assistant initialization script before starting the server
python scripts/init_assistant.py

# Ensure the directory for the PID file exists
mkdir -p /var/pids

# Remove stale PID file, if any
rm -f /var/pids/web.pid

# Start the Flask application with Gunicorn, writing the PID to /var/pids/web.pid
gunicorn --workers=4 --bind=0.0.0.0:8000 --pid /var/pids/web.pid wsgi:app
