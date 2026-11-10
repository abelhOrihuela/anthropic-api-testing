import json
import re
from datetime import date, timedelta
from importlib.metadata import version
from pathlib import Path

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

client = Anthropic()
MODEL = "claude-sonnet-5-5"
DAYS = 7

today = date.today()
since = today - timedelta(days=DAYS)

# Installed versions come from the environment itself, so "does this affect me?" is not a guess.
profile = f"""
Senior full stack engineer. Works with Node.js/TypeScript and Python.
Builds with the Claude API: tool use, web search tool, text editor tool, streaming, RAG with Voyage embeddings.
Installed SDK: anthropic (Python) {version("anthropic")}.
Models used in code: claude-haiku-4-5, claude-sonnet-5-5.
"""

# Restricting domains keeps the digest on primary sources, not blogs repeating the news.
web_search_schema = {
    "type": "web_search_20250305",
    "name": "web_search",
    "max_uses": 8,
    "allowed_domains": ["anthropic.com", "claude.com", "github.com"],
}

system = """
You write a weekly digest for one engineer. Only report items you saw in the search results.
Never guess a date. If a source shows no publication date, leave the item out.
"""

prompt = f"""
Today is {today}. Find what Anthropic published about the Claude API and its SDKs between
{since} and {today}: release notes, new models, deprecations, new tool types, SDK releases.

Reader profile:
{profile}

Give the exact publication date shown on the source, and skip anything older than {since}.
Classify each item for this reader:
- "action": a breaking change, deprecation or retirement that could affect their code
- "try": a new capability they could use in the next weeks
- "info": relevant, but needs nothing from them

At most 10 items, most important first. Reply with only this JSON inside <digest> tags:
<digest>
{{"items": [{{"title": "...", "published": "YYYY-MM-DD", "type": "action | try | info", "why_it_matters": "one sentence for this reader", "url": "source url"}}]}}
</digest>
"""

messages = [{"role": "user", "content": prompt}]

# Every URL the search actually returned, so we can reject links the model made up.
retrieved = set()


def ask():
    response = client.messages.create(
        model=MODEL,
        max_tokens=8000,
        system=system,
        tools=[web_search_schema],
        messages=messages,
    )
    for block in response.content:
        if block.type == "web_search_tool_result" and isinstance(block.content, list):
            retrieved.update(result.url for result in block.content)
    return response


response = ask()

# Server tools can pause long turns; resend the same conversation to continue.
while response.stop_reason == "pause_turn":
    messages.append({"role": "assistant", "content": response.content})
    response = ask()

# Cited answers arrive split across several text blocks, so join them without a separator.
text = "".join(block.text for block in response.content if block.type == "text")

try:
    items = json.loads(re.search(r"<digest>(.*?)</digest>", text, re.DOTALL).group(1))["items"]
except (AttributeError, json.JSONDecodeError, KeyError):
    raise SystemExit(
        f"Could not read the model's answer (stop_reason={response.stop_reason}). Tail: {text[-200:]}"
    )

# The code decides what survives: a visible date inside the window and a URL the search returned.
kept, dropped = [], []
for item in items:
    try:
        in_window = since <= date.fromisoformat(item["published"]) <= today
    except (ValueError, KeyError):
        in_window = False

    if not in_window:
        dropped.append((item, "date outside the window"))
    elif item.get("url") not in retrieved:
        dropped.append((item, "url not returned by the search"))
    else:
        kept.append(item)

sections = [("action", "Requiere acción"), ("try", "Para probar"), ("info", "Informativo")]

markdown = f"# Digest Claude API: {since} a {today}\n"
for kind, heading in sections:
    group = [item for item in kept if item["type"] == kind]
    if not group:
        continue
    markdown += f"\n## {heading}\n"
    for item in group:
        markdown += f"- **{item['title']}** ({item['published']}): {item['why_it_matters']}\n  {item['url']}\n"

file = Path(__file__).parent / f"digest-{today}.md"
file.write_text(markdown)

print(markdown)
print(f"Saved to {file.name}. Kept {len(kept)}, dropped {len(dropped)}.")
for item, reason in dropped:
    print(f"  dropped: {item.get('title')} ({reason})")
