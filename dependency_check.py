import json
import re
import tomllib
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from claude_api import ClaudeClient

client = ClaudeClient()

# Restricting domains keeps the search on primary sources (releases, changelogs, advisories).
web_search_schema = {
    "type": "web_search_20250305",
    "name": "web_search",
    "max_uses": 3,
    "allowed_domains": ["pypi.org", "github.com", "osv.dev"],
}

system = """
You are a release engineer reviewing whether it is safe to upgrade a Python dependency.
Only state facts supported by the search results. If you cannot confirm something, use "unknown".
Do not guess version numbers or advisory IDs.
"""


def installed_versions(project_dir):
    """Direct dependencies from the Pipfile, pinned to what Pipfile.lock actually resolved."""
    pipfile = tomllib.loads((project_dir / "Pipfile").read_text())
    lock = json.loads((project_dir / "Pipfile.lock").read_text())["default"]

    return {
        name: lock[name]["version"].lstrip("=")
        for name in pipfile["packages"]
        if name in lock
    }


def review(package, installed):
    prompt = f"""
The project has {package}=={installed} installed.

1. Find the latest release of {package} on PyPI or GitHub.
2. If it is newer than {installed}, find its changelog or release notes and list the concrete
   breaking changes between the two versions. Do not pad with generic advice like "review the changelog".
3. List any known security advisories that affect {installed}, and say who is affected
   (for example: the library itself, or only a GitHub Action or CLI the project may not use).

Reply with only this JSON inside <report> tags:
<report>
{{
  "package": "{package}",
  "installed": "{installed}",
  "latest": "version or unknown",
  "update_available": true or false,
  "risk": "low | medium | high | unknown",
  "breaking_changes": ["short items, empty if none"],
  "advisories": ["advisory id, who is affected, one line; empty if none"],
  "summary": "one sentence"
}}
</report>
Risk levels:
- "low": no breaking changes and no advisory in the library code itself.
- "medium": advisory affecting only a side component, or minor breaking changes.
- "high": the upgrade needs code changes, or the library code itself has a vulnerability.
- "unknown": you could not find the changelog or release notes. Prefer this over guessing.
"""

    messages = []
    client.add_user_message(messages, prompt)
    response = client.chat(messages, system=system, tools=[web_search_schema])

    # Server tools can pause long turns; resend the same conversation to continue.
    while response.stop_reason == "pause_turn":
        client.add_assistant_message(messages, response)
        response = client.chat(messages, system=system, tools=[web_search_schema])

    # Cited answers arrive split across several text blocks, so join them without a separator.
    text = "".join(b.text for b in response.content if b.type == "text")

    # allowed_domains accepts a whole domain, so drop results from unrelated repos.
    sources = {}
    for block in response.content:
        if block.type == "text" and block.citations:
            for citation in block.citations:
                if package.lower() in citation.url.lower() or "osv.dev" in citation.url:
                    sources[citation.url] = citation.title

    match = re.search(r"<report>(.*?)</report>", text, re.DOTALL)
    try:
        report = json.loads(match.group(1))
    except (AttributeError, json.JSONDecodeError):
        report = {
            "package": package,
            "installed": installed,
            "risk": "unknown",
            "summary": f"Could not parse the report: {text[:200]}",
        }

    return report, sources


def project_code(project_dir):
    """The project's own source with line numbers, so findings can point at file:line."""
    files = sorted(p for p in project_dir.glob("*.py") if p.name != Path(__file__).name)
    return "\n\n".join(
        f"# {path.name}\n"
        + "\n".join(f"{n}: {line}" for n, line in enumerate(path.read_text().splitlines(), 1))
        for path in files
    )


def assess_impact(package, breaking_changes, code):
    """No web search here: this step reads the changelog items against the real code."""
    changes = "\n".join(f"- {change}" for change in breaking_changes)
    prompt = f"""
Upgrading {package} introduces these breaking changes:
{changes}

Here is the project's source code, with line numbers:
<code>
{code}
</code>

For each breaking change, say whether this code is affected. Only report usage you can see
in the code above. Reply with only this JSON inside <impact> tags:
<impact>
[
  {{"change": "short restatement", "affected": "yes | no | unknown", "evidence": "file:line and what is there, empty if none"}}
]
</impact>
"""
    messages = []
    client.add_user_message(messages, prompt)
    response = client.chat(messages)

    text = client.text_from_message(response)
    match = re.search(r"<impact>(.*?)</impact>", text, re.DOTALL)
    try:
        return json.loads(match.group(1))
    except (AttributeError, json.JSONDecodeError):
        return []


if __name__ == "__main__":
    project_dir = Path(__file__).parent
    packages = installed_versions(project_dir)
    print(f"Reviewing {len(packages)} direct dependencies from Pipfile.lock\n")

    with ThreadPoolExecutor(max_workers=len(packages)) as pool:
        results = list(pool.map(lambda item: review(*item), packages.items()))

    order = {"high": 0, "medium": 1, "unknown": 2, "low": 3}
    results.sort(key=lambda result: order.get(result[0].get("risk"), 2))

    # Second step: map each breaking change to the project's own code.
    code = project_code(project_dir)
    with_changes = [r["package"] for r, _ in results if r.get("breaking_changes")]
    with ThreadPoolExecutor(max_workers=max(len(with_changes), 1)) as pool:
        findings = pool.map(
            lambda name: assess_impact(
                name, next(r for r, _ in results if r["package"] == name)["breaking_changes"], code
            ),
            with_changes,
        )
        impacts = dict(zip(with_changes, findings))

    for report, sources in results:
        print(f"[{report.get('risk', 'unknown').upper()}] {report['package']} "
              f"{report['installed']} -> {report.get('latest', 'unknown')}")
        print(f"  {report.get('summary', '')}")
        for item in report.get("breaking_changes", []):
            print(f"  - breaking: {item}")
        for item in report.get("advisories", []):
            print(f"  - advisory: {item}")
        for finding in impacts.get(report["package"], []):
            print(f"  > affects your code? {finding.get('affected')}: {finding.get('change')}")
            if finding.get("evidence"):
                print(f"      {finding['evidence']}")
        for url in sources:
            print(f"  source: {url}")
        print()
