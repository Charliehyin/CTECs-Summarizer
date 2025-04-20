from dotenv import load_dotenv
import os
import json

# Load environment variables
load_dotenv()

# Initialize the base messages once during setup
system_message = """You are analyzing student reviews of courses at Northwestern. 
Use the provided CTEC (Course and Teacher Evaluation Council) data to answer questions about these course reviews.
Base your responses only on the CTEC content provided in the conversation."""

# Read the CTEC file content once
with open("html ctecs/Northwestern - Student Report for COMP_SCI_111-0_2_ Fund Comp Prog (Connor Bain).html", "r") as f:
    ctec_content = f.read()

# Create the base messages
BASE_MESSAGES = [
    {"role": "system", "content": system_message},
    {"role": "user", "content": f"Here is the CTEC content to analyze:\n\n{ctec_content}"}
]

# Save the base messages to a file for app.py to load
with open('base_messages.json', 'w') as f:
    json.dump(BASE_MESSAGES, f)

print("Setup complete. Base messages saved to base_messages.json")