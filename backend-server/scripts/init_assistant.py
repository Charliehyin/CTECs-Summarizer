from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Create the assistant with the desired configuration
assistant = client.beta.assistants.create(
    name="Course Review Assistant",
    instructions="You are analyzing student reviews of courses at Northwestern. Use your knowledge base to answer questions about these course reviews, called CTECs.",
    model="gpt-4o-mini",
    tools=[{"type": "file_search"}],
)

# Create the vector store for file search
vector_store = client.beta.vector_stores.create(name="CTECs")

# Upload the file containing course review data (adjust the file path as necessary)
with open("html ctecs/Northwestern - Student Report for COMP_SCI_111-0_2_ Fund Comp Prog (Connor Bain).html", "rb") as f:
    message_file = client.files.create(
        file=f,
        purpose="assistants"
    )

# Update the assistant with the file search tool resource
assistant = client.beta.assistants.update(
    assistant_id=assistant.id,
    tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}},
)

# Save the configuration (assistant ID, vector store ID, and message file ID) to a file
with open('assistant_config.txt', 'w') as f:
    f.write(f"ASSISTANT_ID={assistant.id}\n")
    f.write(f"VECTOR_STORE_ID={vector_store.id}\n")
    f.write(f"MESSAGE_FILE_ID={message_file.id}\n")

print("Assistant setup complete. Configuration written to assistant_config.txt.")
