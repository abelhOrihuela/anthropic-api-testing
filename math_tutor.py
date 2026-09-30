from claude_api import ClaudeClient

client = ClaudeClient()
system = """
    you are a patient math tutor for kinder garden students.
    Do not directly answer student's questions.
    Guide them to a solution step by step.
"""

messages = []
client.add_user_message(messages, "what is 2+2?")
output = client.chat(messages, system=system)

print(output.content[0].text)
