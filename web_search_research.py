import sys

from claude_api import ClaudeClient

client = ClaudeClient()

web_search_schema = {
    "type": "web_search_20250305",
    "name": "web_search",
    "max_uses": 3,
}

system = """
You are a research assistant helping a candidate prepare for a technical interview.
Only state facts supported by the search results. If you cannot find something, say so.
"""

company = sys.argv[1] if len(sys.argv) > 1 else "Mercado Libre"

prompt = f"""
I have a technical interview next week at {company} for a Senior Full Stack Engineer role.
Research the company and give me a brief with:
1. What the company does and its main products
2. Recent news from the last few months
3. Anything public about its engineering stack or tech blog
4. Two smart questions I could ask the interviewer

Keep it under 250 words.
"""

messages = []
client.add_user_message(messages, prompt)

response = client.chat(messages, system=system, tools=[web_search_schema])

# Server tools can pause long turns; resend the same conversation to continue.
while response.stop_reason == "pause_turn":
    client.add_assistant_message(messages, response)
    response = client.chat(messages, system=system, tools=[web_search_schema])

queries = [b.input["query"] for b in response.content if b.type == "server_tool_use"]

sources = {}
for block in response.content:
    if block.type == "text" and block.citations:
        for citation in block.citations:
            sources[citation.url] = citation.title

print(f"== Searches run ({len(queries)}) ==")
for query in queries:
    print(f"- {query}")

# Cited answers arrive split across several text blocks, so join them without a separator.
brief = "".join(b.text for b in response.content if b.type == "text")

print(f"\n== Brief: {company} ==")
print(brief)

print("\n== Sources ==")
for url, title in sources.items():
    print(f"- {title}: {url}")
