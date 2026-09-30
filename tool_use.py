from datetime import datetime

from claude_api import ClaudeClient

client = ClaudeClient()

get_current_time_schema = {
    "name": "get_current_time",
    "description": "Returns the current time in HH:MM:SS format.",
    "input_schema": {
        "type": "object",
        "properties": {},
    },
}


def get_current_time():
    return datetime.now().strftime("%H:%M:%S")


messages = []
client.add_user_message(messages, "What time is it right now?")

response = client.chat(messages, tools=[get_current_time_schema])
client.add_assistant_message(messages, response)

tool_use_block = next(block for block in response if block.type == "tool_use")
result = get_current_time()

messages.append(
    {
        "role": "user",
        "content": [
            {
                "type": "tool_result",
                "tool_use_id": tool_use_block.id,
                "content": result,
            }
        ],
    }
)

final_response = client.chat(messages, tools=[get_current_time_schema])
print(final_response[0].text)
