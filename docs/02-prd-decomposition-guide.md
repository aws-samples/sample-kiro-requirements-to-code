# PRD Decomposition Guide

## From Product Requirements to Executable Specs

This guide shows how to take a Product Requirements Document and decompose it into a structured set of Kiro specs that can be implemented incrementally.

---

## The Decomposition Hierarchy

```
┌─────────────────────────────────────────────────────────────────┐
│  PRD (Product Requirements Document)                            │
│  Scope: Entire product vision, multi-quarter                    │
│  Owner: Product Owner                                           │
│  Format: sample-prd/product-requirements.md                     │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  Epics (Major Capability Areas)                                 │
│  Scope: Large body of work, often multi-PI                      │
│  Owner: Engineering Lead                                        │
│  Format: .kiro/specs/epic-N-<name>/README.md                    │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  Features (Deliverable Increments)                              │
│  Scope: Completable within one PI (8-12 weeks)                  │
│  Owner: Team                                                    │
│  Format: .kiro/specs/<featureId>-<slug>/                        │
│          (requirements.md, design.md, tasks.md, stories/)       │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  Stories (Implementable Units)                                  │
│  Scope: 1-5 person-days of work                                 │
│  Owner: Individual developer                                    │
│  Format: .kiro/specs/<feature>/stories/<ref>-<id>-<slug>.md     │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  Implementation Tasks (Subtasks within a story)                 │
│  Scope: Hours of work, checkboxes                               │
│  Owner: Developer + Kiro                                        │
│  Format: ## Implementation Tasks section within story file      │
└─────────────────────────────────────────────────────────────────┘
```

---

## Step 1: Analyze the PRD

### What to Look For

Read the PRD and identify:

1. **User personas** — Who uses the system? These map to vertical capabilities.
2. **Core capabilities** — What does the system do? These become epics.
3. **Non-functional requirements** — Performance, security, compliance. These become cross-cutting concerns in steering files and feature design.
4. **Technology constraints** — Mandated stack, cloud provider, compliance frameworks. These go into `technology-guidelines.md` steering.
5. **Delivery timeline** — PIs, milestones, MVP scope. This drives feature prioritization and sprint planning.

### Conversation Starter with Kiro

```
Here's our Product Requirements Document:

[paste PRD or reference file]

Help me:
1. Identify the major epics (capability areas)
2. Understand dependencies between them
3. Suggest a delivery sequence for our first PI
4. Flag any ambiguities or gaps in the requirements
```

### Output: Steering Files

After discussing the PRD, ask Kiro to create steering files:

```
Based on our discussion, please create:
1. .kiro/steering/product-overview.md — the product vision, epics, architecture layers
2. .kiro/steering/technology-guidelines.md — tech constraints we identified
```

These become the persistent context that Kiro uses in every future conversation.

---

## Step 2: Define Epics

### What Makes a Good Epic

| Characteristic | Good | Bad |
|---------------|------|-----|
| Scope | Major capability area | Single feature or user story |
| Duration | Multiple PIs to complete | Done in one sprint |
| Decomposable | Can be split into 3-8 features | Already atomic |
| Independent | Can be delivered incrementally | All-or-nothing |

### Epic README Format

```markdown
# Epic: [Name]

## Vision
One paragraph describing what this epic delivers to users.

## Capabilities
- Capability 1 — brief description
- Capability 2 — brief description

## Features (Planned)
| Feature | PI | Status | Stories |
|---------|----|---------|---------| 
| Feature 1.1 | PI 1 | In Progress | 4 |
| Feature 1.2 | PI 1 | Planned | 3 |
| Feature 1.3 | PI 2 | Future | TBD |

## Dependencies
- Depends on: [other epics or external systems]
- Blocks: [what can't start until this delivers]

## Success Metrics
- Metric 1: [measurable outcome]
- Metric 2: [measurable outcome]
```

### Conversation with Kiro

```
Let's define the epics for our product. From the PRD, I see these
major capability areas:

1. [Area 1] — covers sections X, Y of the PRD
2. [Area 2] — covers sections Z, W of the PRD
3. [Area 3] — cross-cutting infrastructure

Does this decomposition make sense? What am I missing?
```

---

## Step 3: Decompose Features

### What Makes a Good Feature

| Characteristic | Good | Bad |
|---------------|------|-----|
| Scope | Completable in one PI (4-12 weeks) | Spans multiple PIs |
| Deliverable | Produces working software | Only produces documents |
| Testable | Has clear acceptance criteria | Vague "improve X" |
| Independent | Minimal coupling to other in-flight features | Requires 3 other features to land first |

### Feature Folder Contents

When you ask Kiro to create a feature, it produces:

```
.kiro/specs/<featureId>-<slug>/
├── requirements.md      # What we're building and why
├── design.md            # How we're building it (architectural decisions)
├── tasks.md             # Sprint-organized checklist
├── work-item-map.yaml   # Index, capacity, deviations, metadata
└── stories/
    ├── README.md        # Conventions for this feature's stories
    └── *.md             # Individual story files
```

### Requirements.md Structure

```markdown
# Requirements — <Feature Title> (Feature <ID>)

**Tracker Link:** [<ID>](<url>)
**PI:** <PI> · **Effort:** <N> PD · **Owners:** <names>

## Feature Intent
[What this feature delivers — from tracker or PRD]

## In Scope (this PI)
- Deliverable 1
- Deliverable 2

## Out of Scope (this PI)
- Explicitly excluded item 1
- Deferred to next PI item 2

## Requirements Traceability

| Req | Description | PRD Section | Stories (PD) |
|-----|-------------|-------------|--------------|
| R1  | Description | §2.3        | A1 (3)       |
| R2  | Description | §4.1        | A2 (2), A3 (3) |

**Total effort:** <N> PD · **Stories:** <count>
```

### Design.md Structure

```markdown
# Design — <Feature Title> (Feature <ID>)

## Summary
What this PI delivers vs the full product vision.

## Architectural Decisions

### DEC-001 — <Title>
- **Context:** Why this decision is needed
- **Decision:** What we chose
- **Alternatives considered:** What we rejected and why
- **Consequences:** Impact and tradeoffs
- **Rollback path:** How to reverse if needed

## Component Diagram
[Mermaid diagram showing component relationships]

## Sequencing
Sprint-by-sprint delivery plan explaining why stories are ordered this way.

## Open Questions / Risks
1. Question or risk with mitigation plan
```

### Conversation with Kiro

```
Let's decompose Epic 1 (User Management) into features for PI 1.

Context:
- We have 12 weeks (3 sprints of 4 weeks)
- Team capacity: 2 engineers, ~20 PD per sprint
- MVP must include: authentication, basic RBAC, tenant isolation

What features do you suggest, and how should we sequence them?
```

---

## Step 4: Create Stories

### What Makes a Good Story

| Characteristic | Good | Bad |
|---------------|------|-----|
| Size | 1-5 person-days | >5 PD or <0.5 PD |
| Scope | One logical unit of work | Kitchen sink |
| Acceptance criteria | Specific, testable Given/When/Then | Vague "it works" |
| Dependencies | Minimal, explicitly declared | Hidden implicit deps |
| Deliverable | Produces mergeable PR with working code | Preparatory work only |

### Story File Format

```markdown
---
trackerId: pending      # Tracker ID (or "pending" before sync)
ref: A1                 # Short internal reference
parent: 12345           # Parent feature tracker ID
title: "Descriptive title covering the what"
state: New              # New | Active | Done | Closed
sprint: S1              # Sprint assignment
owner: developer-name   # Individual owner
effort: 3               # Person-days
priority: 2
tags: [auth, api, PI1]
dependsOn: []           # [A1, A2] if dependencies exist
lastSync: 1970-01-01T00:00:00Z
---

## Context
One sentence placing this story in the feature and PI.

## Goal
As a <role>, I want <capability> so that <outcome>.

## Scope
- What's included in this story
- Specific deliverables

## Out of Scope
- What's explicitly excluded

## Dependencies
- None (or list what must be done first)

## Acceptance Criteria
- **Given** precondition, **When** action, **Then** expected result.
- **Given** precondition, **When** action, **Then** expected result.
```

### Story Naming Convention

```
<ref>-<trackerId>-<slug>.md
```

- `ref`: Letter prefix (from feature) + sequence number (A1, A2, I1, I2)
- `trackerId`: Work-item ID from tracker (or "pending")
- `slug`: Kebab-case summary

Examples:
- `A1-pending-oauth2-provider.md` (before tracker sync)
- `A1-12345-oauth2-provider.md` (after tracker sync)

### Conversation with Kiro

```
Let's create stories for Feature 101 (Authentication).

Design context:
- We chose OAuth2 with Cognito (DEC-001)
- RBAC with policy-based authorization (DEC-002)
- Tenant isolation via JWT claims (DEC-003)

Team:
- Alice: auth specialist, available all 3 sprints
- Bob: infra focus, sprint 1-2 only

How should we decompose this into stories?
```

---

## Step 5: Add Implementation Tasks

### When to Add Tasks

Implementation tasks are added **after** discussing the approach with Kiro, not during initial story creation. The flow:

1. Pick up a story
2. Discuss implementation approach with Kiro
3. Agree on the plan
4. Kiro adds `## Implementation Tasks` to the story file
5. Execute tasks (Kiro writes code, checks boxes)

### Task Format

```markdown
## Implementation Tasks

### Task 1: <Logical grouping>
Description of what this group accomplishes.

- [ ] 1.1 Specific subtask with clear deliverable
- [ ] 1.2 Another subtask
- [ ] 1.3 Another subtask

### Task 2: <Next logical grouping>
- [ ] 2.1 Subtask
- [ ] 2.2 Subtask

### Task N: Validation
- [ ] N.1 Linting passes
- [ ] N.2 Tests pass (if applicable)
- [ ] N.3 Security scan clean
- [ ] N.4 Build succeeds
- [ ] N.5 Acceptance criteria verified manually
```

### Task Granularity Guidelines

| Too coarse | Just right | Too fine |
|-----------|-----------|---------|
| "Implement the API" | "Create POST /users endpoint with validation" | "Add line 47 to users.controller.ts" |
| "Set up infrastructure" | "Create VPC module with public/private subnets" | "Add Name tag to subnet resource" |
| "Write tests" | "Add integration tests for auth flow" | "Assert status code is 200" |

### Conversation with Kiro

```
I'm starting story A1 (OAuth2 Provider Integration).

Context from design.md:
- Using AWS Cognito as the IdP
- Standard OAuth2 Authorization Code + PKCE flow
- Token validation middleware in FastAPI

Let's discuss the implementation approach. I'm thinking:
1. Cognito Terraform module first
2. Then the FastAPI middleware
3. Then integration tests

What do you think? Anything I'm missing?
```

---

## Common Decomposition Patterns

### Pattern 1: Infrastructure-First

For features that need AWS resources before app code:

```
Story 1: Terraform module (infra)
Story 2: CI/CD pipeline (devops)
Story 3: Application code (app)
Story 4: Integration + testing (validation)
```

### Pattern 2: Vertical Slice

For features that can be delivered end-to-end in thin slices:

```
Story 1: Minimal happy path (API + basic infra + tests)
Story 2: Error handling and edge cases
Story 3: Security hardening
Story 4: Performance optimization
```

### Pattern 3: Spike-Then-Implement

For features with significant unknowns:

```
Story 1: SPIKE — research + decision (time-boxed, produces ADR)
Story 2-N: Implementation (informed by spike outcome)
```

### Pattern 4: Foundation-Then-Extend

For platform capabilities consumed by multiple features:

```
Story 1: Core foundation (module layout, interfaces)
Story 2: First consumer integration
Story 3: Second consumer integration
Story 4: Monitoring + operational readiness
```

---

## Tips for Effective Decomposition

1. **Start with outcomes, not tasks** — "Users can log in with SSO" not "Configure Cognito"
2. **Each story should be demo-able** — Can you show something working after it's done?
3. **Dependencies flow forward** — Sprint 1 stories should not depend on Sprint 2 stories
4. **Leave room for discovery** — Plan 80% capacity, keep 20% for unknowns
5. **Spike early** — If there's a technology question, answer it in Sprint 1
6. **Group by risk** — High-risk stories early, so you have time to course-correct
7. **Cross-cutting concerns are features** — Don't scatter observability, security, CI/CD across other features; give them their own stories
