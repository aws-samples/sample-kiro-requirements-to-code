# Epic [N]: [Epic Title]

<!-- Copy this template to .kiro/specs/epic-N-<slug>/README.md and fill in the brackets.
     Kiro creates and maintains this file after your initial epic-extraction conversation.
     Do not edit YAML front-matter in story files by hand — tell Kiro what to change. -->

## Vision

[One paragraph describing what this epic delivers from the user's perspective.
Why does it matter? What problem does it solve? What does success look like?]

## Capabilities

<!-- Bullet list of user-facing capabilities this epic covers. Aim for 4-8 items.
     These become the scope boundary for feature decomposition in Phase 2. -->

- [Capability 1]
- [Capability 2]
- [Capability 3]

## Features

<!-- One row per feature. Add rows as features are decomposed from this epic.
     Status: Planned | In Progress | Done
     Effort is summed from the feature's work-item-map.yaml. -->

| Feature | ID | PI | Status | Stories | Effort |
|---------|----|----|--------|---------|--------|
| [Feature Name] | [NNN] | [PI-1] | Planned | [N] | [N PD] |

## Dependencies

<!-- Which other epics or external systems does this epic depend on?
     Which epics are blocked until this one delivers? Be specific — "needs VPC before
     ECS can deploy" is more useful than "depends on infra". -->

- Depends on: [Epic N — reason]
- Blocks: [Epic N — reason]

## Out of Scope

<!-- Explicitly list things that belong to a later PI or a different epic.
     This prevents scope creep during feature decomposition. -->

- [Deferred item 1] — PI [N]
- [Deferred item 2] — PI [N]

## Success Metrics

<!-- Measurable outcomes that indicate this epic is done. Prefer quantified metrics
     (latency, error rate, coverage %) over subjective statements ("feels fast").
     These become the acceptance criteria for the epic as a whole. -->

- [Metric 1, e.g. "P99 API latency < 200ms under 100 concurrent users"]
- [Metric 2, e.g. "Zero cross-tenant data leakage in penetration testing"]
- [Metric 3]
