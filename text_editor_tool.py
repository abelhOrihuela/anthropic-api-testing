import subprocess
import sys
import tempfile
from pathlib import Path

from claude_api import ClaudeClient

client = ClaudeClient()

# Anthropic defines the schema; this code implements what each command does.
text_editor_schema = {
    "type": "text_editor_20250728",
    "name": "str_replace_based_edit_tool",
}

BUGGY_CODE = """def cart_total(prices, discount_percent):
    subtotal = sum(prices)
    discount = subtotal * discount_percent
    return subtotal - discount
"""


def resolve_path(root, path):
    # Every path is relative to the workspace; anything that escapes it is rejected.
    full_path = (root / path.lstrip("/")).resolve()
    if not full_path.is_relative_to(root):
        raise PermissionError("Path is outside the workspace")
    return full_path


def run_command(root, command):
    action = command["command"]
    path = resolve_path(root, command["path"])

    if action == "view":
        if path.is_dir():
            return "\n".join(sorted(p.name for p in path.iterdir()))
        lines = path.read_text().splitlines()
        start, end = command.get("view_range") or [1, -1]
        end = len(lines) if end == -1 else min(end, len(lines))
        return "\n".join(f"{n}: {lines[n - 1]}" for n in range(start, end + 1))

    if action == "create":
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(command["file_text"])
        return f"Created {command['path']}"

    if action == "str_replace":
        text = path.read_text()
        matches = text.count(command["old_str"])
        if matches == 0:
            raise ValueError(
                "No match found for replacement. Please check your text and try again."
            )
        if matches > 1:
            raise ValueError(
                f"Found {matches} matches for replacement text. Please provide more context to make a unique match."
            )
        path.write_text(text.replace(command["old_str"], command["new_str"]))
        return "Successfully replaced text at exactly one location."

    if action == "insert":
        lines = path.read_text().splitlines(keepends=True)
        lines.insert(command["insert_line"], command["insert_text"])
        path.write_text("".join(lines))
        return "Successfully inserted text."

    raise ValueError(f"Unsupported command: {action}")


messages = []
client.add_user_message(
    messages,
    "cart.py has a bug: cart_total([100, 50], 10) should apply a 10% discount "
    "and return 135.0, but it returns a negative number. Fix it.",
)

with tempfile.TemporaryDirectory() as workspace:
    root = Path(workspace).resolve()
    (root / "cart.py").write_text(BUGGY_CODE)

    response = client.chat(messages, tools=[text_editor_schema])

    while response.stop_reason == "tool_use":
        client.add_assistant_message(messages, response)

        results = []
        for block in response.content:
            if block.type != "tool_use":
                continue

            print(f"-> {block.input['command']} {block.input.get('path', '')}")

            try:
                content, is_error = run_command(root, block.input), False
            except (OSError, ValueError, KeyError) as error:
                content, is_error = f"Error: {error}", True

            results.append(
                {
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": content,
                    "is_error": is_error,
                }
            )

        client.add_user_message(messages, results)
        response = client.chat(messages, tools=[text_editor_schema])

    print("\n== Claude says ==")
    print(client.text_from_message(response))

    print("\n== cart.py after the edit ==")
    print((root / "cart.py").read_text())

    # The code doesn't opine: run it and check the number.
    check = subprocess.run(
        [
            sys.executable,
            "-c",
            "from cart import cart_total; print(cart_total([100, 50], 10))",
        ],
        cwd=root,
        capture_output=True,
        text=True,
        timeout=5,
    )
    print("== Verification ==")
    print(
        f"cart_total([100, 50], 10) -> {check.stdout.strip() or check.stderr.strip()}"
    )
