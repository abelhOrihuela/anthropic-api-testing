from claude_api import ClaudeClient


client = ClaudeClient()

messages = []

client.add_user_message(messages, "Write a one paragraph guide to recursion")
response = client.chat(messages=messages, thinking=True)

print(response)