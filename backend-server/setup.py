from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Read the CTEC file content
with open("html ctecs/Northwestern - Student Report for COMP_SCI_111-0_2_ Fund Comp Prog (Connor Bain).html", "rb") as f:
    ctec_content = f.read().decode('utf-8')

# You can use the chat completion API directly
response = client.chat.completions.create(
    model="gpt-4o-mini",  # Using GPT-4 instead of gpt-4o-mini since that seems to be a typo
    messages=[
        {
            "role": "system",
            "content": "You are analyzing student reviews of courses at Northwestern. Use your knowledge base to answer questions about these course reviews, called CTECs."
        },
        {
            "role": "user",
            "content": f"Here is the CTEC content to analyze: {ctec_content}"
        }
    ]
)

# If you need to save any configuration
with open('api_config.txt', 'w') as f:
    f.write("Using standard OpenAI API\n")