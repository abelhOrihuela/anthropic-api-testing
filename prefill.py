import json
from claude_api import ClaudeClient

client = ClaudeClient()


def without_prefill():
    """Without prefill: the model usually wraps the JSON in explanations and markdown."""
    messages = []
    client.add_user_message(
        messages,
        "Generate a JSON object with 3 programming languages and their creation year.",
    )
    response = client.chat(messages)
    return response[0].text


def with_prefill():
    """
    With prefill: we write the start of the assistant's response ourselves
    ("```json") and use stop_sequences to cut off right before the closing fence.
    The result is pure JSON, ready for json.loads().
    """
    messages = []
    client.add_user_message(
        messages,
        "Generate a JSON object with 3 programming languages and their creation year.",
    )
    client.add_assistant_message(messages, "```json")

    response = client.chat(messages, stop_sequences=["```"])
    return response[0].text


if __name__ == "__main__":
    print("== Without prefill ==")
    response = without_prefill()
    print(response)

    print("\n== With prefill ==")
    response = with_prefill()
    print(response)

    data = json.loads(response)
    print("\nParsed successfully:", data)
