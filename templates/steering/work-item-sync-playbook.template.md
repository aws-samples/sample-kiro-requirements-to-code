---
inclusion: manual
---

# Work-Item Sync Playbook

Attach with `#work-item-sync-playbook` when syncing story files with your tracker.

## Source of Truth

Story files are source of truth for content. Tracker is source of truth for state transitions.

## Owner Aliases

| Alias | Display Name | Tracker Identity |
|-------|-------------|-----------------|
| [alias1] | [Full Name] | [email or ID] |
| [alias2] | [Full Name] | [email or ID] |

## Sprint Aliases

| Alias | Tracker Iteration / Milestone |
|-------|-------------------------------|
| S1 | [Full iteration path or milestone name] |
| S2 | [Full iteration path or milestone name] |
| S3 | [Full iteration path or milestone name] |

## Field Defaults

| Field | Default Value |
|-------|--------------|
| Work item type | [Story / Issue / Task] |
| State (new) | [New / open] |
| Priority | [default] |
| Area/Project | [path or name] |

## Sync Rules

### Push (Create)
1. Story file has `trackerId: pending`
2. Show payload to user
3. On approval: create work item, update file with ID, rename file

### Push (Update)
1. Read current tracker state
2. Compute minimal diff
3. Show diff, get approval
4. Apply patch, update lastSync

### Pull (Drift Check)
1. Read all tracker items in scope
2. Compare vs files since lastSync
3. Show drift, user decides per field
4. Apply choices, update lastSync

## Rules

- Never write to tracker without explicit approval
- State transitions are human-driven
- Update lastSync after every sync
