from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

assistant = client.beta.assistants.create(
    name="Course Review Assistant",
    instructions="You are analyzing student reviews of courses at Northwestern. Use your knowledge base to answer questions about these course reviews, called CTECs.",
    model="gpt-4o-mini",
    tools=[{"type": "file_search"}],
)

vector_store = client.beta.vector_stores.create(name="CTECs")

message_file = client.files.create(
    file=open("html ctecs/Northwestern - Student Report for COMP_SCI_111-0_2_ Fund Comp Prog (Connor Bain).html", "rb"),
    purpose="assistants"
)

assistant = client.beta.assistants.update(
    assistant_id=assistant.id,
    tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}},
)

with open('assistant_config.txt', 'w') as f:
    f.write(f"ASSISTANT_ID={assistant.id}\n")
    f.write(f"VECTOR_STORE_ID={vector_store.id}\n")
    f.write(f"MESSAGE_FILE_ID={message_file.id}\n")