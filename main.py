from openai import OpenAI
import time
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

file_paths = ["html ctecs/Northwestern - Student Report for COMP_SCI_111-0_2_ Fund Comp Prog (Connor Bain).html"]
file_streams = [open(path, "rb") for path in file_paths]

message_file = client.files.create(
  file=open("html ctecs/Northwestern - Student Report for COMP_SCI_111-0_2_ Fund Comp Prog (Connor Bain).html", "rb"), purpose="assistants"
)

assistant = client.beta.assistants.update(
  assistant_id=assistant.id,
  tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}},
)

user_input = input("You: ")

thread = client.beta.threads.create(
  messages=[
    {
      "role": "user",
      "content": user_input,
      "attachments": [
        { "file_id": message_file.id, "tools": [{"type": "file_search"}] }
      ],
    }
  ]
)

run = client.beta.threads.runs.create(
    thread_id=thread.id,
    assistant_id=assistant.id
)

while True:
    run_status = client.beta.threads.runs.retrieve(
        thread_id=thread.id,
        run_id=run.id
    )
    if run_status.status == 'completed':
        break
    time.sleep(1) 

messages = client.beta.threads.messages.list(thread_id=thread.id)

for message in messages.data:
    if message.role == "assistant":
        print(message.content[0].text.value)