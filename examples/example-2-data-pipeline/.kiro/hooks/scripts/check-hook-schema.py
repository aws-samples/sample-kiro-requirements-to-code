#!/usr/bin/env python3
"""Validate Kiro hook files against the v1 schema.

Catches the mistakes that are easy to make when hand-writing hooks, including
the IDE 0.x legacy shape (`when`/`then`, camelCase events, glob `patterns`)
which silently fails to load.

Usage
  python3 check-hook-schema.py                 # validate .kiro/hooks/*.json
  python3 check-hook-schema.py path [path ...] # validate specific files or dirs

Exit codes
  0  all files valid
  1  at least one file invalid
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

VALID_TRIGGERS = {
    "SessionStart",
    "Stop",
    "UserPromptSubmit",
    "PreToolUse",
    "PostToolUse",
    "PostFileCreate",
    "PostFileSave",
    "PostFileDelete",
    "PreTaskExec",
    "PostTaskExec",
}

# Triggers whose matcher is ignored by Kiro.
NO_MATCHER = {"SessionStart", "Stop", "PreTaskExec", "PostTaskExec"}

# Triggers where a command action may block by exiting 2.
BLOCKING = {"PreToolUse", "UserPromptSubmit", "PreTaskExec"}

# IDE 0.x names -> v1 replacements.
LEGACY_TRIGGERS = {
    "fileEdited": "PostFileSave",
    "fileCreated": "PostFileCreate",
    "fileDeleted": "PostFileDelete",
    "preToolUse": "PreToolUse",
    "postToolUse": "PostToolUse",
    "promptSubmit": "UserPromptSubmit",
    "agentSpawn": "SessionStart",
    "agentStop": "Stop",
    "preTaskExecution": "PreTaskExec",
    "postTaskExecution": "PostTaskExec",
    "userTriggered": "(no v1 equivalent - use a manual steering file)",
}

LEGACY_ACTIONS = {"askAgent": "agent", "runCommand": "command"}

GLOB_HINT = re.compile(r"\*\*|/\*")


def validate_file(path: Path) -> list[str]:
    problems: list[str] = []

    if path.suffix != ".json":
        problems.append(
            f"filename must end in .json (found '{path.suffix}'). "
            f"'.kiro.hook' is the IDE 0.x format and will not load as a v1 hook."
        )

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return problems + [f"invalid JSON: {exc}"]

    if not isinstance(data, dict):
        return problems + ["top level must be an object"]

    # Legacy file shape: top-level name/when/then instead of version/hooks.
    if "when" in data or "then" in data:
        problems.append(
            "this is the IDE 0.x hook shape (top-level 'when'/'then'). "
            "Wrap hooks in {\"version\": \"v1\", \"hooks\": [...]} and use "
            "'trigger'/'matcher'/'action'."
        )
        return problems

    version = data.get("version")
    if version != "v1":
        problems.append(
            f"version must be the string \"v1\" (found {version!r}). "
            f"Semver values like \"1.0.0\" are not valid."
        )

    hooks = data.get("hooks")
    if not isinstance(hooks, list) or not hooks:
        problems.append("'hooks' must be a non-empty array")
        return problems

    for index, hook in enumerate(hooks):
        label = f"hooks[{index}]"
        if not isinstance(hook, dict):
            problems.append(f"{label}: must be an object")
            continue

        name = hook.get("name")
        if not name or not isinstance(name, str):
            problems.append(f"{label}: 'name' is required")
        else:
            label = f"hooks[{index}] '{name}'"

        for legacy_key in ("when", "then"):
            if legacy_key in hook:
                problems.append(
                    f"{label}: '{legacy_key}' is the IDE 0.x key; use "
                    f"'{'trigger' if legacy_key == 'when' else 'action'}'"
                )

        if "patterns" in hook:
            problems.append(
                f"{label}: 'patterns' is not a v1 field. Use a single 'matcher' "
                f"regex instead of a glob array."
            )
        if "toolTypes" in hook:
            problems.append(
                f"{label}: 'toolTypes' is not a v1 field. Put the tool name in "
                f"'matcher' (for example \"write\")."
            )

        trigger = hook.get("trigger")
        if not trigger:
            problems.append(f"{label}: 'trigger' is required")
        elif trigger in LEGACY_TRIGGERS:
            problems.append(
                f"{label}: trigger '{trigger}' is the IDE 0.x name; use "
                f"'{LEGACY_TRIGGERS[trigger]}'"
            )
        elif trigger not in VALID_TRIGGERS:
            problems.append(
                f"{label}: unknown trigger '{trigger}'. Valid: "
                f"{', '.join(sorted(VALID_TRIGGERS))}"
            )

        matcher = hook.get("matcher")
        if matcher is not None:
            if not isinstance(matcher, str):
                problems.append(f"{label}: 'matcher' must be a string regex")
            else:
                try:
                    re.compile(matcher)
                except re.error as exc:
                    problems.append(f"{label}: 'matcher' is not a valid regex: {exc}")
                if GLOB_HINT.search(matcher) and "\\" not in matcher:
                    problems.append(
                        f"{label}: matcher '{matcher}' looks like a glob. Matchers "
                        f"are regexes: use '^src/.*\\.ts$' rather than 'src/**/*.ts'."
                    )
            if trigger in NO_MATCHER:
                problems.append(
                    f"{label}: trigger '{trigger}' ignores 'matcher'; remove it to "
                    f"avoid implying the hook is filtered."
                )

        action = hook.get("action")
        if not isinstance(action, dict):
            problems.append(f"{label}: 'action' object is required")
        else:
            action_type = action.get("type")
            if action_type in LEGACY_ACTIONS:
                problems.append(
                    f"{label}: action type '{action_type}' is not valid; use "
                    f"'{LEGACY_ACTIONS[action_type]}'"
                )
            elif action_type not in ("command", "agent"):
                problems.append(
                    f"{label}: action.type must be 'command' or 'agent' "
                    f"(found {action_type!r})"
                )
            elif action_type == "command" and not action.get("command"):
                problems.append(f"{label}: command action requires 'command'")
            elif action_type == "agent" and not action.get("prompt"):
                problems.append(f"{label}: agent action requires 'prompt'")

            if action_type == "agent" and "timeout" in hook:
                problems.append(
                    f"{label}: 'timeout' is ignored for agent actions; remove it."
                )

        timeout = hook.get("timeout")
        if timeout is not None and (not isinstance(timeout, int) or timeout < 0):
            problems.append(f"{label}: 'timeout' must be a non-negative integer (seconds)")

        enabled = hook.get("enabled")
        if enabled is not None and not isinstance(enabled, bool):
            problems.append(f"{label}: 'enabled' must be true or false")

    return problems


def collect(targets: list[str]) -> list[Path]:
    if not targets:
        default = Path(".kiro/hooks")
        return sorted(default.glob("*.json")) if default.is_dir() else []
    files: list[Path] = []
    for target in targets:
        path = Path(target)
        if path.is_dir():
            files.extend(sorted(path.glob("**/*.json")))
            files.extend(sorted(path.glob("**/*.kiro.hook")))
        elif path.exists():
            files.append(path)
        else:
            print(f"WARNING no such path: {path}", file=sys.stderr)
    return files


def main(argv: list[str]) -> int:
    files = collect(argv)
    if not files:
        print("No hook files found.")
        return 0

    failures = 0
    for path in files:
        problems = validate_file(path)
        if problems:
            failures += 1
            print(f"FAIL {path}", file=sys.stderr)
            for problem in problems:
                print(f"       {problem}", file=sys.stderr)
        else:
            print(f"OK   {path}")

    print(f"\n{len(files) - failures}/{len(files)} hook files valid.")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
