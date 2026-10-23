---
inclusion: manual
---

# PR Conventions

Attach with `#pr-conventions` when opening, reviewing, or landing a pull request.

## Branches

| Purpose | Pattern | Example |
|---------|---------|---------|
| Story work | `story/<ref>-<slug>` | `story/[REF]-[SHORT-SLUG]` |
| Bug fix | `fix/<tracker-id>-<slug>` | `fix/[TRACKER-ID]-[SHORT-SLUG]` |
| Spike | `spike/<ref>-<slug>` | `spike/[REF]-[SHORT-SLUG]` |
| Infra only | `infra/<ref>-<slug>` | `infra/[REF]-[SHORT-SLUG]` |

`<ref>` is the story ref from the story front matter (`ref: [REF]`), not the tracker ID — the ref exists before the work item does. Slugs are lowercase and hyphenated, [MAX-SLUG-WORDS] words max. One branch per story: a branch spanning two stories cannot be reviewed or reverted cleanly. `[DEFAULT-BRANCH]` is protected, so direct pushes are rejected.

## Commits

Conventional commits, one logical change each:

```
<type>(<scope>): <imperative summary>

[Optional body: why, not what]

Work-Item: [TRACKER-ID]
```

- Types: `feat`, `fix`, `chore`, `docs`, `test`, `refactor`, `infra`.
- Scope is the module or service (`[SCOPE-EXAMPLE]`).
- Summary in the imperative, [MAX-SUBJECT-LENGTH] characters max, no trailing period.
- The `Work-Item:` trailer keeps the tracker link greppable from `git log` alone. Note what CI actually enforces: the `work-item-link-check` workflow verifies the tracker ID in the **PR title, body, or branch name** — the commit trailer is convention, not the gate. Put `Work-Item: [TRACKER-ID]` in the PR body too and both stay satisfied.

## Pull Requests

Title: `[[TRACKER-ID]] <short summary>` — the bracketed ID makes the tracker link scannable in the merge queue.

Description sections, all required:

| Section | Content |
|---------|---------|
| Story | Link to `.kiro/specs/<feature>/stories/<file>` plus the tracker ID |
| What changed | Bullets, reviewer-facing, not a commit dump |
| Why | The requirement or design section driving it |
| How to test | Exact commands or steps a reviewer can run |
| Deviations | Differences from `design.md`, or "None". Record anything material as an ADR in `docs/decisions/` |
| Risk | Blast radius, rollback path, migration or feature-flag notes |

Every PR links back to its story file and its tracker ID. Without both, traceability from requirement to code breaks and the PR is closed unreviewed.

## Required Checks

All blocking on `[DEFAULT-BRANCH]`:

- `[LINT-COMMAND]`, `[TYPE-CHECK-COMMAND]`, `[TEST-COMMAND]` green; coverage at or above [COVERAGE-PERCENT]%.
- `[SECURITY-SCAN-COMMAND]` clean at [SEVERITY-THRESHOLD] and above.
- `terraform fmt -check`, `tflint`, `checkov` for any `infra/**` change, with `plan` output posted as a comment.
- Every story task checked off in the story file.
- [REVIEWER-COUNT] approval(s), including a [PATH-OWNER-RULE] owner for [OWNED-PATHS].

## Merging

- [MERGE-STRATEGY] into `[DEFAULT-BRANCH]`, with the tracker ID kept in the resulting subject line.
- Keep PRs under roughly [MAX-CHANGED-LINES] changed lines. Split larger work by story; review quality falls off a cliff past that.
- Author merges after approval, then syncs story state to the tracker per `#work-item-sync-playbook`.
- Delete the branch on merge.
