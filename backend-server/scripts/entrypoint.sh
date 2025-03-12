#!/bin/sh
# Run the assistant initialization script before starting the server
/home/ec2-user/CTECs-Summarizer/venv/bin/python3.12 /home/ec2-user/CTECs-Summarizer/backend-server/scripts/init_assistant.py
# python scripts/compute_embeddings.py

# Ensure the directory for the PID file exists
# mkdir -p /var/pids

# Remove stale PID file, if any
# rm -f /var/pids/web.pid

# Start the Flask application with Gunicorn
cd /home/ec2-user/CTECs-Summarizer/backend-server
/home/ec2-user/CTECs-Summarizer/venv/bin/gunicorn --workers=4 --bind=0.0.0.0:8000 wsgi:app
