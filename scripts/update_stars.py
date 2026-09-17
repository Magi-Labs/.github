#!/usr/bin/env python3
"""Refresh the org profile's total stars. Requires Python 3 and authenticated gh."""
import json
from pathlib import Path
import re
import subprocess

ORG = "Magi-Labs"
README = Path(__file__).resolve().parents[1] / "profile" / "README.md"
START = "<!-- org-stars:start -->"
END = "<!-- org-stars:end -->"


def main():
    pages = json.loads(subprocess.check_output([
        "gh", "api", "--paginate", "--slurp",
        f"orgs/{ORG}/repos?type=public&per_page=100",
    ], text=True))
    repos = {repo["id"]: repo for page in pages for repo in page if not repo["private"]}
    total = sum(repo["stargazers_count"] for repo in repos.values())
    block = f"{START}\n⭐ **{total:,} total stars** across our public repositories.\n{END}"
    original = README.read_text()
    if original.count(START) != 1 or original.count(END) != 1:
        raise ValueError("README must contain exactly one org-stars marker pair")
    updated, count = re.subn(re.escape(START) + r".*?" + re.escape(END), lambda _: block, original, flags=re.S)
    if count != 1:
        raise ValueError("Invalid org-stars marker order")
    if updated != original:
        README.write_text(updated)
    print(f"{ORG}: {total:,} stars across {len(repos)} public repositories")


if __name__ == "__main__":
    main()
