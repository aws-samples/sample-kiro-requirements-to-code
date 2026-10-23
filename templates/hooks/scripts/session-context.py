#!/usr/bin/env python3
"""Print current working context at session start.

Wired to a SessionStart hook. On exit 0, STDOUT is added to the agent's context,
so this is a cheap way to tell Kiro which branch you are on and which stories
are in flight before you type anything.

Copy to .kiro/hooks/scripts/session-context.py.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

SPECS_DIR = Path(".kiro/specs")
FRONT_MATTER = re.compile(r"\A---\r?\n(.*?)\r?\n---", re.DOTALL)
# Compared case-insensitively via .title(), matching check-spec-integrity.py's
# tolerance for `state: active` vs the documented `state: Active`.
TRACKED_STATES = ("Active", "New")


def git(*args: str) -> str:
    try:
        result = subprocess.run(
            ["git", *args], capture_output=True, text=True, timeout=5, check=False
        )
        return result.stdout.strip() if result.returncode == 0 else ""
    except (OSError, subprocess.SubprocessError):
        return ""


def front_matter(text: str) -> dict[str, str]:
    match = FRONT_MATTER.search(text)
    if not match:
        return {}
    fields: dict[str, str] = {}
    for line in match.group(1).splitlines():
        line = line.split("#", 1)[0].rstrip()
        if ":" not in line or line.lstrip().startswith("#"):
            continue
        key, _, value = line.partition(":")
        fields[key.strip()] = value.strip().strip('"')
    return fields


def main() -> int:
    branch = git("rev-parse", "--abbrev-ref", "HEAD") or "unknown"
    print(f"Branch: {branch}")

    dirty = git("status", "--porcelain")
    if dirty:
        print(f"Uncommitted changes: {len(dirty.splitlines())} file(s)")

    if not SPECS_DIR.is_dir():
        return 0

    by_state: dict[str, list[str]] = {state: [] for state in TRACKED_STATES}
    for story in sorted(SPECS_DIR.glob("*/stories/*.md")):
        if story.name.upper() == "README.MD":
            continue
        fields = front_matter(story.read_text(encoding="utf-8"))
        state = fields.get("state", "").strip().title()
        if state not in by_state:
            continue
        ref = fields.get("ref", "?")
        owner = fields.get("owner", "unassigned")
        sprint = fields.get("sprint", "-")
        title = fields.get("title", story.stem)
        by_state[state].append(f"  {ref} [{sprint}] {title} ({owner})")

    for state in TRACKED_STATES:
        entries = by_state[state]
        if entries:
            print(f"\nStories {state}:")
            print("\n".join(entries))

    if not any(by_state.values()):
        print("\nNo Active or New stories.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
