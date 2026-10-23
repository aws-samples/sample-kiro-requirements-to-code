#!/usr/bin/env python3
"""Verify that spec files, task checklists and work-item maps agree.

This is the enforcement mechanism behind spec-driven development at team scale.
Manual discipline holds for two developers reviewing each other's PRs; it does
not hold for twenty-five. Run this as a PostFileSave hook while editing specs
and as a required CI check on every pull request.

Checks performed
  E1  every story listed in work-item-map.yaml exists on disk
  E2  every story file on disk is listed in work-item-map.yaml
  E3  every story ref in tasks.md resolves to a story file
  E4  every dependsOn ref resolves to a story somewhere in the repo
  E5  a story marked Done has no unchecked implementation tasks
  E6  story refs are globally unique across all features
  E7  a story cannot depend on itself, and dependency cycles are reported
  E8  every story file carries a 'ref' in its front matter
  W1  effort totals in work-item-map.yaml capacity match the sum of story effort
  W2  a story marked Done has been synced to the tracker
  W3  a story with every task checked has been moved to Done

Exit codes
  0  no errors (warnings may still be printed)
  1  at least one error, or any warning when --strict is passed

Stdlib only and no YAML dependency, so it runs in a hook and in CI unmodified.
Copy to .kiro/hooks/scripts/check-spec-integrity.py.
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import defaultdict
from pathlib import Path

SPECS_DIR = Path(".kiro/specs")

FRONT_MATTER = re.compile(r"\A---\r?\n(.*?)\r?\n---", re.DOTALL)
# Matches: A1: { trackerId: 12345, file: stories/A1-12345-slug.md }
MAP_STORY = re.compile(
    r"^\s{2}([A-Za-z][A-Za-z0-9]*)\s*:\s*\{[^}]*?file\s*:\s*([^,}\s]+)", re.MULTILINE
)
# Matches a bolded ref at the start of a task line: - [x] **A1 — Title**
TASK_REF = re.compile(r"^\s*-\s*\[[ x~]\]\s*\*\*([A-Za-z][A-Za-z0-9]*)\s*[—-]", re.MULTILINE)
CHECKBOX = re.compile(r"^\s*-\s*\[([ x~])\]", re.MULTILINE)
IMPL_HEADING = re.compile(r"^##\s+Implementation Tasks\s*$", re.MULTILINE)

DONE_STATES = {"done", "closed"}


class Story:
    __slots__ = ("path", "ref", "state", "effort", "tracker_id", "depends_on", "feature")

    def __init__(self, path: Path, feature: str, fm: dict[str, str], body: str) -> None:
        self.path = path
        self.feature = feature
        self.ref = fm.get("ref", "")
        self.state = fm.get("state", "").strip().lower()
        self.tracker_id = fm.get("trackerId", "").strip()
        self.depends_on = parse_ref_list(fm.get("dependsOn", ""))
        try:
            self.effort = int(fm.get("effort", "0") or 0)
        except ValueError:
            self.effort = 0


def parse_front_matter(text: str) -> dict[str, str]:
    """Parse the flat `key: value` front matter the story template defines."""
    match = FRONT_MATTER.search(text)
    if not match:
        return {}
    fields: dict[str, str] = {}
    for line in match.group(1).splitlines():
        line = line.split("#", 1)[0].rstrip()
        if not line.strip() or line.lstrip().startswith("#") or ":" not in line:
            continue
        key, _, value = line.partition(":")
        fields[key.strip()] = value.strip().strip('"')
    return fields


def parse_ref_list(raw: str) -> list[str]:
    """Parse a YAML inline list such as [A1, I2] into ['A1', 'I2']."""
    raw = raw.strip()
    if not raw or raw in ("[]", "~", "null"):
        return []
    return [item.strip().strip("\"'") for item in raw.strip("[]").split(",") if item.strip()]


def implementation_tasks(text: str) -> list[str]:
    """Return checkbox states from the Implementation Tasks section only."""
    match = IMPL_HEADING.search(text)
    if not match:
        return []
    return CHECKBOX.findall(text[match.end() :])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--strict", action="store_true", help="treat warnings as errors"
    )
    parser.add_argument(
        "--specs-dir", default=str(SPECS_DIR), help="path to .kiro/specs"
    )
    args = parser.parse_args()

    specs = Path(args.specs_dir)
    if not specs.is_dir():
        print(f"No spec directory at {specs}; nothing to check.")
        return 0

    errors: list[str] = []
    warnings: list[str] = []
    stories_by_ref: dict[str, list[Story]] = defaultdict(list)

    feature_dirs = sorted(p.parent for p in specs.glob("*/work-item-map.yaml"))
    if not feature_dirs:
        print(f"No feature folders with work-item-map.yaml under {specs}.")
        return 0

    for feature_dir in feature_dirs:
        feature = feature_dir.name
        map_path = feature_dir / "work-item-map.yaml"
        map_text = map_path.read_text(encoding="utf-8")
        mapped = dict(MAP_STORY.findall(map_text))

        stories_dir = feature_dir / "stories"
        on_disk: dict[str, Story] = {}
        if stories_dir.is_dir():
            for story_path in sorted(stories_dir.glob("*.md")):
                if story_path.name.upper() == "README.MD":
                    continue
                text = story_path.read_text(encoding="utf-8")
                fm = parse_front_matter(text)
                if not fm.get("ref"):
                    errors.append(
                        f"[E8] {story_path}: no 'ref' in front matter, cannot be tracked"
                    )
                    continue
                story = Story(story_path, feature, fm, text)
                on_disk[story.ref] = story
                stories_by_ref[story.ref].append(story)

                # E5: state must agree with the task checkboxes
                boxes = implementation_tasks(text)
                if boxes:
                    all_done = all(box == "x" for box in boxes)
                    is_done = story.state in DONE_STATES
                    if is_done and not all_done:
                        open_count = sum(1 for box in boxes if box != "x")
                        errors.append(
                            f"[E5] {story_path}: state is '{fm.get('state')}' but "
                            f"{open_count} of {len(boxes)} implementation tasks are unchecked"
                        )
                    if all_done and not is_done:
                        warnings.append(
                            f"[W3] {story_path}: all {len(boxes)} tasks are checked but "
                            f"state is '{fm.get('state')}'"
                        )
                # W2: Done work should be reflected in the tracker
                if story.state in DONE_STATES and story.tracker_id in ("pending", ""):
                    warnings.append(
                        f"[W2] {story_path}: state is Done but trackerId is "
                        f"'{story.tracker_id or 'missing'}' — never synced"
                    )

        # E1: mapped stories must exist
        for ref, rel_path in sorted(mapped.items()):
            target = feature_dir / rel_path
            if not target.is_file():
                errors.append(
                    f"[E1] {map_path}: story {ref} maps to '{rel_path}' which does not exist"
                )

        # E2: stories on disk must be mapped
        for ref, story in sorted(on_disk.items()):
            if ref not in mapped:
                errors.append(
                    f"[E2] {map_path}: story {ref} exists at "
                    f"{story.path.relative_to(feature_dir)} but is not listed"
                )

        # E3: task refs must resolve
        tasks_path = feature_dir / "tasks.md"
        if tasks_path.is_file():
            for ref in sorted(set(TASK_REF.findall(tasks_path.read_text(encoding="utf-8")))):
                if ref not in on_disk:
                    errors.append(
                        f"[E3] {tasks_path}: references story {ref}, which has no story file"
                    )

        # W1: capacity totals should match story effort
        total_match = re.search(r"^\s*total\s*:\s*\{[^}]*?total\s*:\s*(\d+)", map_text, re.MULTILINE)
        if total_match and on_disk:
            declared = int(total_match.group(1))
            actual = sum(story.effort for story in on_disk.values())
            mapped_only = len(on_disk) == len(mapped)
            if mapped_only and declared != actual:
                warnings.append(
                    f"[W1] {map_path}: capacity total is {declared} PD but story "
                    f"effort sums to {actual} PD"
                )

    # E6: refs must be globally unique
    for ref, stories in sorted(stories_by_ref.items()):
        if len(stories) > 1:
            locations = ", ".join(str(s.path) for s in stories)
            errors.append(
                f"[E6] ref '{ref}' is used by {len(stories)} stories: {locations}. "
                f"Refs are referenced globally by dependsOn and must be unique."
            )

    # E4 / E7: dependency references
    all_refs = set(stories_by_ref)
    for ref, stories in sorted(stories_by_ref.items()):
        for story in stories:
            for dep in story.depends_on:
                if dep == ref:
                    errors.append(f"[E7] {story.path}: story {ref} depends on itself")
                elif dep not in all_refs:
                    errors.append(
                        f"[E4] {story.path}: dependsOn references '{dep}', "
                        f"which is not a story in this repo"
                    )

    # E7: dependency cycles
    graph = {ref: stories[0].depends_on for ref, stories in stories_by_ref.items()}
    for cycle in find_cycles(graph, all_refs):
        errors.append(f"[E7] dependency cycle: {' -> '.join(cycle)}")

    for line in errors:
        print(f"ERROR   {line}", file=sys.stderr)
    for line in warnings:
        print(f"WARNING {line}", file=sys.stderr)

    checked = sum(len(v) for v in stories_by_ref.values())
    summary = (
        f"Checked {checked} stories across {len(feature_dirs)} features: "
        f"{len(errors)} errors, {len(warnings)} warnings."
    )
    if errors or (warnings and args.strict):
        print(summary, file=sys.stderr)
        return 1
    print(summary)
    return 0


def find_cycles(graph: dict[str, list[str]], known: set[str]) -> list[list[str]]:
    """Return one representative path per dependency cycle."""
    cycles: list[list[str]] = []
    seen_signatures: set[frozenset[str]] = set()
    state: dict[str, int] = {}

    def visit(node: str, path: list[str]) -> None:
        state[node] = 1
        for dep in graph.get(node, []):
            if dep not in known:
                continue
            if state.get(dep) == 1:
                cycle = path[path.index(dep) :] + [dep]
                signature = frozenset(cycle)
                if signature not in seen_signatures:
                    seen_signatures.add(signature)
                    cycles.append(cycle)
            elif state.get(dep, 0) == 0:
                visit(dep, path + [dep])
        state[node] = 2

    for node in sorted(graph):
        if state.get(node, 0) == 0:
            visit(node, [node])
    return cycles


if __name__ == "__main__":
    sys.exit(main())
