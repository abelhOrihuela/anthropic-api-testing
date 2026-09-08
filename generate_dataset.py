import json

# start client
from claude_api import ClaudeClient

client = ClaudeClient()
messages = []

def generate_dataset():
    # prompt = """
    #     Generate an evaluation dataset for a prompt evaluation. The dataset will be used to evaluate prompts that generate Python, JSON, or Regex specifically for AWS-related tasks. Generate an array of JSON objects, each representing task that requires Python, JSON, or a Regex to complete.

    #     Example output:
    #     ```json
    #     [
    #     {
    #         "task": "Description of task",
    #         "format": "json" or "python" or "regex",
    #         "solution_criteria": "Key criteria for evaluating the solution"
    #     },
    #     ...additional
    #     ]
    #     ```

    #     * Focus on tasks that can be solved by writing a single Python function, a single JSON object, or a single regex
    #     * Focus on tasks that do not require writing much code

    #     Please generate 3 objects.
    # """
    messages = []
    client.add_user_message(messages, prompt)
    client.add_assistant_message(messages, "```json")
    text = client.chat(messages, stop_sequences=["```"])
    
    return json.loads(text)

dataset = generate_dataset()

with open('dataset.json', 'w') as f:
    json.dump(dataset, f, indent=2)