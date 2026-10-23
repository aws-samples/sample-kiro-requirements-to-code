---
inclusion: manual
---

# Work-Item Sync Playbook

Attach with `#work-item-sync-playbook` when you want Kiro to push changes from spec files to the work-item tracker, or pull changes back.

## Source of Truth

Story files at `.kiro/specs/<feature>/stories/<ref>-<trackerId>-<slug>.md` are the source of truth for:
- Story metadata (front-matter)
- Description (body above `## Acceptance Criteria`)
- Acceptance criteria (`## Acceptance Criteria` section)

The tracker is source of truth for:
- State transitions
- Creation timestamps
- Parent links

## Owner Aliases

| Alias | Display Name | Tracker Identity |
|-------|-------------|-----------------|
| alice | Alice Chen | alice.chen@example.com |
| bob | Bob Martinez | bob.martinez@example.com |
| carol | Carol Kim | carol.kim@example.com |

## Sprint Aliases

| Alias | Tracker Iteration / Milestone |
|-------|-------------------------------|
| S1 | PI-1 Sprint 1 |
| S2 | PI-1 Sprint 2 |
| S3 | PI-1 Sprint 3 |
| PI1 | PI-1 (unassigned to sprint) |

## Field Defaults

| Field | Default Value |
|-------|--------------|
| Work item type | Story (ADO) / Issue (GitHub) |
| State (new) | New / open |
| Priority | 2 |
| Area/Label | taskflow |

## Sync Flows

### Push: Story File → Tracker (Create)

1. Story file has `trackerId: pending`
2. Verify parent feature exists
3. Show full payload (title, description, AC, sprint, owner, effort, tags)
4. On approval: create work item
5. Update `trackerId` in front-matter
6. Rename file to include tracker ID
7. Update work-item-map.yaml

### Push: Story File → Tracker (Update)

1. Read current tracker state
2. Compute minimal diff (only changed fields)
3. Show: field | tracker value | story file value
4. On approval: apply minimal patch
5. Update `lastSync`

### Pull: Tracker → Story File (Drift Check)

1. Read tracker work items for stories in scope
2. Compare vs story files (since `lastSync`)
3. Show drift per field
4. User chooses: accept tracker | overwrite tracker | skip
5. Apply choices, update `lastSync`

## Rules

- Never write to tracker without explicit approval
- State transitions are human-driven
- Batch reads (parallel), individual writes (sequential)
- Update `lastSync` after every successful sync
