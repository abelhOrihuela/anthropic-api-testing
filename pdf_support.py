from claude_api import ClaudeClient
import base64

with open("images/earth.pdf", "rb") as f:
    pdf_data = base64.standard_b64encode(f.read()).decode("utf-8")

messages = []
client = ClaudeClient()


client.add_user_message(messages, [
    {
        "type": "document",
        "source": {
            "type": "base64",
            "media_type": "application/pdf",
            "data": pdf_data
        }
    },
    {
        "type": "text",
        "text": "Summarize the doc in two sentences"
    }
])

response = client.chat(messages)

print(response)
