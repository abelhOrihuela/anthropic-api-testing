from dotenv import load_dotenv
from anthropic import Anthropic

# load env variables
load_dotenv()

# start client
client = Anthropic()
model = "claude-haiku-4-5"

messages = []


def add_user_message(messages, text):
    message = {"role": "user", "content": text}
    messages.append(message)


def add_assistant_message(messages, text):
    message = {"role": "assistant", "content": text}
    messages.append(message)


def chat(messages, system: None):

    params = {
        "model": model,
        "max_tokens": 1000,
        "messages": messages,
    }

    if system:
        params["system"] = system

    message = client.messages.create(**params)
    return message.content[0].text


# add_user_message(messages, "what is DLQ in IT?, Answer in one sentence")
# answer = chat(messages)
# add_assistant_message(messages, answer)

# add_user_message(messages, "create a new answer")
# answer = chat(messages)

# add_assistant_message(messages, answer)

# print(messages)


print("== Welcome to my bot ==")
print("to close session type 'q' \n")
print("do you need help? \n")
while True:

    system = """
    you are a patient math tutor for kinder garden students.
    Do not directly answer student's questions.
    Guide them to a solution step by step.
        """

    user_input = input("Type your question: ")
    print(">", user_input)

    if user_input == "q":
        break
    add_user_message(messages, user_input)
    answer = chat(messages, system)

    add_assistant_message(messages, answer)
    print("----")
    print(answer)
    print("----")
