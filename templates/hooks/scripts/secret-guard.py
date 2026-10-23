#!/usr/bin/env python3
"""Block agent file writes that contain credential-shaped strings.

Wired to a PreToolUse hook with matcher "write". Kiro passes the hook event as
JSON on STDIN. Exit 2 blocks the tool call and returns STDERR to the agent.

Copy to .kiro/hooks/scripts/secret-guard.py alongside secret-guard.json.
"""

from __future__ import annotations

import json
import re
import sys

# Patterns are deliberately conservative: each one should almost never fire on
# legitimate source code. Add project-specific patterns as you find them.
PATTERNS: dict[str, str] = {
    "an AWS access key ID": r"(?:AKIA|ASIA)[0-9A-Z]{16}",
    "a private key block": r"-----BEGIN (?:[A-Z ]+ )?PRIVATE KEY-----",
    "a hardcoded credential assignment": (
        r"(?i)\b(?:password|passwd|secret|api[_-]?key|token)\b\s*[:=]\s*"
        r"[\"'][^\"'\s]{8,}[\"']"
    ),
    "a Slack token": r"xox[baprs]-[0-9A-Za-z-]{10,}",
    "a GitHub personal access token": r"gh[pousr]_[0-9A-Za-z]{36,}",
}

# Files where credential-shaped strings are expected and harmless.
ALLOWLIST = (
    ".kiro/hooks/scripts/secret-guard.py",
    "templates/hooks/scripts/secret-guard.py",
)

# Placeholder values that look like secrets but are documentation, not leaks.
PLACEHOLDER = re.compile(
    r"(?i)(example|placeholder|changeme|your[_-]?|dummy|redacted|xxx+|\<[^>]+\>)"
)


def iter_strings(value: object) -> "list[str]":
    """Collect every string value in a nested structure.

    Scanning raw values matters: json.dumps would escape embedded quotes as \\",
    which breaks patterns that expect a quote right after the assignment.
    """
    found: list[str] = []
    if isinstance(value, str):
        found.append(value)
    elif isinstance(value, dict):
        for item in value.values():
            found.extend(iter_strings(item))
    elif isinstance(value, (list, tuple)):
        for item in value:
            found.extend(iter_strings(item))
    return found


def main() -> int:
    try:
        event = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        # Malformed event: fail open rather than blocking legitimate work.
        return 0

    tool_input = event.get("tool_input") or {}
    path = str(tool_input.get("path") or tool_input.get("file_path") or "")

    if any(path.endswith(allowed) for allowed in ALLOWLIST):
        return 0

    hits = []
    for label, pattern in PATTERNS.items():
        for chunk in iter_strings(tool_input):
            match = re.search(pattern, chunk)
            if match and not PLACEHOLDER.search(match.group(0)):
                hits.append(label)
                break

    if not hits:
        return 0

    target = path or "this file"
    sys.stderr.write(
        f"Blocked write to {target}: the content appears to contain "
        f"{', '.join(hits)}.\n"
        "Move the value to AWS Secrets Manager or SSM Parameter Store and "
        "reference it at runtime. If this is a placeholder, make that explicit "
        "(for example EXAMPLE_KEY or <your-token>) and retry.\n"
    )
    return 2


if __name__ == "__main__":
    sys.exit(main())
