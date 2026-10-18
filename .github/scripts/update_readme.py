"""Rewrite the "Recently active" block of README.md from the GitHub GraphQL API."""

import json
import os
import re
import urllib.request
from datetime import datetime
from pathlib import Path

LOGIN = "sarah-majdoub"
LIMIT = 6

# Public, but not what the profile should lead with.
EXCLUDE = {
    "sarah-majdoub/sarah-majdoub",
    "sarah-majdoub/gitops-tp",
    "sarah-majdoub/Insat-Library",
}

# Team repos whose owners haven't set a description yet.
FALLBACK_DESCRIPTIONS = {
    "Maher-Wali/Mental-Health-Companion": "RAG mental-health companion with hybrid retrieval and crisis detection",
    "Maher-Wali/projet-bigdata": "NYC taxi big-data pipeline: HDFS, Kafka, Spark Structured Streaming",
    "tarek-gritli/house-pricing": "House price prediction on scraped Tunisian listings",
}

# Their default branch isn't the one with the project on it.
URL_OVERRIDES = {
    "Maher-Wali/projet-bigdata": "https://github.com/Maher-Wali/projet-bigdata/tree/bigdata-pipeline",
}

REPO_FIELDS = "nameWithOwner url description pushedAt isFork primaryLanguage { name }"
QUERY = f"""
query($login: String!) {{
  user(login: $login) {{
    repositories(first: 30, privacy: PUBLIC, ownerAffiliations: OWNER,
                 orderBy: {{field: PUSHED_AT, direction: DESC}}) {{
      nodes {{ {REPO_FIELDS} }}
    }}
    repositoriesContributedTo(first: 30, privacy: PUBLIC, includeUserRepositories: false,
                              contributionTypes: [COMMIT, PULL_REQUEST],
                              orderBy: {{field: PUSHED_AT, direction: DESC}}) {{
      nodes {{ {REPO_FIELDS} }}
    }}
  }}
}}
"""

START, END = "<!-- RECENT:START -->", "<!-- RECENT:END -->"


def fetch():
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": LOGIN}}).encode(),
        headers={"Authorization": f"bearer {os.environ['GITHUB_TOKEN']}"},
    )
    with urllib.request.urlopen(req) as resp:
        body = json.load(resp)
    if "errors" in body:
        raise SystemExit(body["errors"])
    user = body["data"]["user"]
    return user["repositories"]["nodes"] + user["repositoriesContributedTo"]["nodes"]


def render(repos):
    rows = []
    for r in sorted(repos, key=lambda r: r["pushedAt"], reverse=True):
        name = r["nameWithOwner"]
        if r["isFork"] or name in EXCLUDE:
            continue
        owner, short = name.split("/")
        label = f"**{short}**" + ("" if owner == LOGIN else " (team)")
        url = URL_OVERRIDES.get(name, r["url"])
        desc = (r["description"] or FALLBACK_DESCRIPTIONS.get(name, "")).replace("|", "\\|")
        lang = (r["primaryLanguage"] or {}).get("name", "")
        date = datetime.fromisoformat(r["pushedAt"].replace("Z", "+00:00")).strftime("%-d %b %Y")
        rows.append(f"| [{label}]({url}) | {desc} | {lang} | {date} |")
        if len(rows) == LIMIT:
            break
    table = ["| Repo | What it is | Language | Last update |", "|---|---|---|---|", *rows]
    return "\n".join(table)


def main():
    readme = Path("README.md")
    text = readme.read_text()
    block = f"{START}\n{render(fetch())}\n{END}"
    new = re.sub(re.escape(START) + r".*?" + re.escape(END), lambda _: block, text, flags=re.S)
    if START not in text:
        raise SystemExit("README.md has no RECENT markers")
    readme.write_text(new)


if __name__ == "__main__":
    main()
