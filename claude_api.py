from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()


class ClaudeClient:
    def __init__(self, model="claude-haiku-4-5"):
        self.client = Anthropic()
        self.model = model

    def add_user_message(self, messages, text):
        messages.append({
            "role": "user",
            "content": text
        })

    def add_assistant_message(self, messages, text):
        messages.append({
            "role": "assistant",
            "content": text
        })

    def chat(self, messages, system=None, stop_sequences=None):
        params = {
            "model": self.model,
            "max_tokens": 1000,
            "messages": messages,
        }

        if system:
            params["system"] = system

        if stop_sequences:
            params["stop_sequences"] = stop_sequences

        message = self.client.messages.create(**params)
        return message.content[0].text
