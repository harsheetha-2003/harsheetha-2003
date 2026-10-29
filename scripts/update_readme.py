#!/usr/bin/env python3
"""Refresh the auto-generated "More Repositories" block in README.md.

Lists your public, non-fork repositories (most recently pushed first) that are
not already linked somewhere else in the README. Everything between the
REPOS:START and REPOS:END markers is rewritten; the rest is left untouched.
"""
import json
import os
import re
import urllib.request

USER = "harsheetha-2003"
README = "README.md"
START = "<!-- REPOS:START -->"
END = "<!-- REPOS:END -->"
MAX_ITEMS = 8


def fetch_repos():
    url = f"https://api.github.com/users/{USER}/repos?per_page=100&sort=pushed&type=owner"
    req = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "readme-updater",
        },
    )
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def already_listed(url, text):
    # Match the repo URL but not a longer repo name that starts the same way.
    return re.search(re.escape(url) + r"(?![\w-])", text, re.IGNORECASE) is not None


def build_block(repos, outside_text):
    items = []
    for repo in repos:
        if repo.get("fork") or repo.get("archived") or repo.get("private"):
            continue
        if repo["name"].lower() == USER.lower():  # the profile repo itself
            continue
        if already_listed(repo["html_url"], outside_text):
            continue
        line = f"- [{repo['name']}]({repo['html_url']})"
        desc = (repo.get("description") or "").strip()
        if desc:
            line += f" – {desc}"
        if repo.get("language"):
            line += f" · `{repo['language']}`"
        items.append(line)
        if len(items) == MAX_ITEMS:
            break
    if not items:
        return ""
    return "\n## 📂 More Repositories\n\n" + "\n".join(items) + "\n\n"


def main():
    with open(README, encoding="utf-8") as f:
        text = f.read()
    if START not in text or END not in text:
        raise SystemExit("README.md is missing the REPOS:START / REPOS:END markers.")

    head, rest = text.split(START, 1)
    _, tail = rest.split(END, 1)

    block = build_block(fetch_repos(), head + tail)
    new_text = head + START + block + END + tail

    if new_text != text:
        with open(README, "w", encoding="utf-8") as f:
            f.write(new_text)
        print("README.md updated.")
    else:
        print("No changes.")


if __name__ == "__main__":
    main()
