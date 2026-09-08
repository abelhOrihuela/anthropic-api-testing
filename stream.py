from dotenv import load_dotenv
from anthropic import Anthropic

# load env variables
load_dotenv()

# start client
client = Anthropic()
model = "claude-haiku-4-5"

messages = []

def add_user_message(messages, text):
    message = {
        "role": "user",
        "content": text
    }

    messages.append(message)
def add_assistant_message(messages, text):
    message = {
        "role": "assistant",
        "content": text
    }

    messages.append(message)


add_user_message(messages, "Write a 1 sentence description of a fakedatabase")

params = {
    "model": model,
    "max_tokens": 1000,
    "messages": messages
    }

with client.messages.stream(
    **params
) as stream:

    for text in stream.text_stream:
        #print(text, end="")
        pass


print(stream.get_final_message().content[0])


