---
# Tracker identity
trackerId: pending              # Integer/string once created, or "pending"
ref: X0                         # Short internal ref (e.g. A1, I2)
parent: 0                       # Parent feature tracker ID
title: "Short, descriptive title"

# Scheduling
state: New                      # New | Active | Done | Closed | Removed
sprint: S1                      # S1 | S2 | S3 | PI1
owner: alice                    # See owner aliases in sync playbook
effort: 0                       # Integer, person-days

# Classification
priority: 2
tags: []                        # YAML list
dependsOn: []                   # List of refs, e.g. [A1, I2]

# Sync tracking
lastSync: 1970-01-01T00:00:00Z
---

## Context

One sentence placing this story in its feature and PI.

## Goal

As a <role>, I want <capability> so that <outcome>.

## Scope

- Deliverable 1
- Deliverable 2

## Out of Scope

- Excluded item 1

## Dependencies

- None

## Acceptance Criteria

- **Given** precondition, **When** action, **Then** expected result.
- **Given** precondition, **When** action, **Then** expected result.
