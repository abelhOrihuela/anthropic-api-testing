from claude_api import ClaudeClient

client = ClaudeClient()

web_search_schema = {
    "type": "web_search_20250305",
    "name": "web_search",
    "max_uses": 5
}

messages = []
message = """
    what is the best exercise to gaining leg muscle? chek latest news
"""
client.add_user_message(messages, message)
output = client.chat(messages, tools=[web_search_schema])

print(output)
