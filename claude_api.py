from dotenv import load_dotenv
from anthropic import Anthropic
from anthropic.types import Message

load_dotenv()


class ClaudeClient:
    def __init__(self, model="claude-haiku-4-5"):
        self.client = Anthropic()
        self.model = model

    def add_user_message(self, messages, message):
        messages.append(
            {
                "role": "user",
                "content": message.content if isinstance(message, Message) else message,
            }
        )

    def add_assistant_message(self, messages, message):
        messages.append(
            {
                "role": "assistant",
                "content": message.content if isinstance(message, Message) else message,
            }
        )

    def chat(self, messages, system=None, stop_sequences=None, tools=None):
        params = {
            "model": self.model,
            "max_tokens": 1000,
            "messages": messages,
        }

        if system:
            params["system"] = system

        if stop_sequences:
            params["stop_sequences"] = stop_sequences

        if tools:
            params["tools"] = tools

        message = self.client.messages.create(**params)

        return message

    def text_from_message(self, message):
        return "\n".join(
            [block.text for block in message.content if block.type == "text"]
        )
