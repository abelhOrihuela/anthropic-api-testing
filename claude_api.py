from dotenv import load_dotenv
from anthropic import Anthropic
from anthropic.types import Message


class ClaudeClient:
    def __init__(self, model="claude-haiku-4-5"):
        load_dotenv()

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

    def chat(self, messages, system=None, stop_sequences=None, tools=None, thinking =False, thinking_budget=1024):
        params = {
            "model": self.model,
            "max_tokens": 4000,
            "messages": messages,
        }

        if thinking:
            params["thinking"] = {
                "type": "enabled",
                "budget_tokens": thinking_budget
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
