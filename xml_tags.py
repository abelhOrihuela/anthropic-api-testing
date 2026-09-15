from claude_api import ClaudeClient

client = ClaudeClient()

task = "Write a function that reverses a string"
solution = "def reverse(s): return s[::-1]"
criteria = "The solution must handle empty strings and unicode characters"

# XML tags delimit each block clearly, no matter how long or unusual its content is.
prompt = f"""
Evaluate the following solution.

<task>
{task}
</task>

<solution>
{solution}
</solution>

<criteria>
{criteria}
</criteria>
"""

messages = []
client.add_user_message(messages, prompt)

response = client.chat(messages)
print(response[0].text)
