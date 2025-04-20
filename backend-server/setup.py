from dotenv import load_dotenv
import os
import json

load_dotenv()

system_message = """You are analyzing student reviews of courses at Northwestern. 
Use the provided CTEC (Course and Teacher Evaluation Council) data to answer questions about these course reviews.
Base your responses only on the CTEC content provided in the conversation."""

try:
    with open("html ctecs/Northwestern - Student Report for COMP_SCI_111-0_2_ Fund Comp Prog (Connor Bain).html", "r") as f:
        ctec_content = f.read()

    BASE_MESSAGES = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": f"Here is the CTEC content to analyze:\n\n{ctec_content}"}
    ]

    with open('base_messages.json', 'w') as f:
        json.dump(BASE_MESSAGES, f)

    print("Setup complete. Base messages saved to base_messages.json")
except Exception as e:
    print(f"Error during setup: {str(e)}")
    exit(1)