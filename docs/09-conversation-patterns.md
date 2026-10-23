# Conversation Patterns

## Overview

The spec-driven workflow is conversational. You discuss with Kiro, Kiro formalizes the
outcome into files. This guide gives you real prompt examples for every phase of the
workflow — copy, adapt, and use them as starting points.

These are patterns, not scripts. The goal is to give Kiro enough context to produce
useful artifacts without requiring you to write perfect prompts from scratch.

---

## Phase 1: PRD Intake

### Starting the decomposition

```
Here's our Product Requirements Document:

[paste PRD or use: "The PRD is in sample-prd/product-requirements.md"]

Help me break it down. Specifically:
1. What are the major epics (3–5 capability areas)?
2. What are the dependencies between them?
3. What's a sensible delivery sequence for our first PI (12 weeks)?
4. Are there any gaps or ambiguities I should resolve with the product owner?
```

### After discussing the PRD

```
Based on our discussion, please create the following files:

1. .kiro/steering/product-overview.md — vision, epics, architecture layers,
   key terminology, NFRs from the PRD
2. .kiro/steering/technology-guidelines.md — the tech constraints we identified
   (Python 3.12, FastAPI, ECS Fargate, Aurora, Cognito, Terraform)

Use "always" inclusion for both files.
```

### Verifying the steering files

```
Read back the product-overview.md you just created. Does it capture:
- The multi-tenant model correctly?
- The four epics with their capability lists?
- The NFRs (latency, security, availability)?

If not, what needs adjusting?
```

---

## Phase 2: Feature Decomposition

### Decomposing an epic into features

```
Let's decompose Epic 1 (User & Tenant Management) into features for PI 1.

Context:
- PI 1 is 12 weeks, 3 sprints of 4 weeks each
- Team: Alice (auth specialist) and Bob (infra focus, sprint 1–2 only)
- Capacity: ~20 person-days per sprint, 60 total
- MVP must include: authentication, RBAC, and tenant isolation
- Social login, MFA, SSO federation are explicitly PI 2

Propose the features, their effort estimates, and sequencing.
Highlight any dependencies between features.
```

### Creating a feature folder

```
Let's create the spec folder for Feature 101 (Authentication & Authorization).

From our discussion:
- It covers requirements §Security, §Epic 1 in the PRD
- Stories: Cognito Terraform (A1), JWT middleware (A2), RBAC (A3), tenant isolation (A4)
- Total effort: ~14 person-days
- Owner split: Alice (infra/RBAC), Bob (middleware/tenant)

Please create:
- .kiro/specs/101-authentication/requirements.md — with the PRD traceability table
- .kiro/specs/101-authentication/design.md — three decisions: IdP choice, JWT library
  approach, RBAC pattern
- .kiro/specs/101-authentication/tasks.md — sprint checklist
- .kiro/specs/101-authentication/work-item-map.yaml
```

### Reviewing a proposed design decision

```
For DEC-002 (RBAC approach), I want to think through the options:

Option A: FastAPI Depends with a role enum and hierarchy
Option B: Policy-based with a simple rules engine (cedar-policy or similar)
Option C: Attribute-based with permission tables in the database

For our scale (2-person team, MVP in 12 weeks), what are the tradeoffs?
Which fits our constraints?
```

---

## Phase 3: Story Creation

### Creating stories for a feature

```
Let's create the stories for Feature 101 (Authentication & Authorization).

Team context:
- Alice: platform engineer, strong Terraform and Python, sprint 1–3
- Bob: backend developer, strong Python/FastAPI, sprint 1–2 only

Constraints:
- Stories should be 2–4 person-days each
- Infrastructure stories come before the code that depends on them
- Each story must be independently mergeable (no half-complete features per PR)

Please create story files for A1–A4 with YAML front-matter, context, goal,
scope, out of scope, dependencies, and acceptance criteria.
Don't add implementation tasks yet — we'll do that during sprint planning.
```

### Refining a story's acceptance criteria

```
Story A2 (JWT middleware) has this acceptance criterion:

  "Given a valid JWT, When a request hits a protected endpoint,
   Then the middleware validates it."

That's too vague. Help me make it more specific:
- What exactly does "validates" mean? (signature, expiry, audience, issuer)
- What does "protected endpoint" mean? (the FastAPI Depends pattern)
- What should the response look like on failure? (RFC 7807? custom JSON?)
```

### Splitting a story that's too large

```
Story A3 (RBAC) is currently 5 person-days, which is too large.

Looking at the scope:
- Role enum and hierarchy
- require_role dependency factory
- Audit logging on permission denial
- Tests for all role combinations

Can we split this into two stories of 2–3 days each without creating
a dependency that blocks Sprint 2?
```

### Syncing stories to the tracker

```
Please create all the Feature 101 stories in our Azure DevOps project.

Before calling any API, show me the payload you plan to send for each story
so I can review and approve. Field mapping is in the sync playbook.
```

---

## Phase 4: Sprint Planning (Adding Implementation Tasks)

### Opening a planning conversation

```
I'm planning Sprint 2 for Feature 101. Let's discuss the implementation
approach for story A3 (RBAC) before I add tasks.

Current state:
- A2 is Done: CurrentUser has a `role: str` field from the JWT claim
- A3 scope: require_role dependency, role hierarchy, audit logging, tests

I'm thinking:
1. Add a Role enum to models.py with a hierarchy dict
2. require_role(minimum_role: Role) → Callable factory in dependencies.py
3. On insufficient role: log structured audit entry, raise AuthorizationError
4. Tests: all role × endpoint combinations

Does that cover everything? What am I missing from the acceptance criteria?
```

### After agreeing on the approach

```
Good. Now add ## Implementation Tasks to story A3 based on our discussion.

The tasks should:
- Be grouped by logical theme (not file-by-file)
- Be specific enough that Kiro can execute each one
- Always end with a Validation task group covering ruff, mypy, pytest, and
  manual AC verification
- Not duplicate work already done in A2
```

### Reviewing the generated tasks before committing

```
Review the implementation tasks you just added to A3. Check:
1. Do they cover all five acceptance criteria?
2. Is the order correct (can each task execute after the previous one)?
3. Is anything missing from the test tasks?
4. Is the Validation task group complete?
```

---

## Phase 5: Implementation

### Starting a story

```
I'm starting story A3 (RBAC, ADO-12303). The branch is story/ADO-12303-rbac.

Let's execute the implementation tasks in order. Start with Task 1 (Role
enum and hierarchy). Read the current models.py first so we don't
contradict what A2 already built.
```

### Handling an unexpected decision during implementation

```
I just realized that the Role enum needs to be in a shared module that
both the JWT middleware (A2) and the RBAC dependency (A3) can import,
but A2 already shipped with role as a plain str.

Options:
1. Update A2's CurrentUser.role type to Role enum — requires updating
   the already-merged A2 code and tests
2. Keep role as str in CurrentUser, parse to Role enum at the dependency
   layer in A3
3. Add Role to models.py now (it belongs there anyway) and update A2's
   tests to use it

Which approach is cleanest? If we pick option 1 or 3, is this a deviation
from the design that needs to be recorded in work-item-map.yaml?
```

### Checking a task off and moving to the next

```
Task 1 is done. The Role enum and ROLE_HIERARCHY are in models.py,
all tests pass. Mark task 1 complete in the story file and let's move
to Task 2 (require_role factory).
```

### Stuck on an acceptance criterion

```
I can't figure out how to satisfy this acceptance criterion:

  "Given a permission denial, When the response is sent, Then a structured
   log entry is emitted with user_id, tenant_id, required_role, actual_role,
   endpoint."

How do I get the endpoint path inside a FastAPI Depends? The Request object
isn't injected automatically.
```

---

## Phase 6: Review and Delivery

### Preparing the PR

```
Story A3 is done. All tasks are checked off in the story file.
Update state to Done and help me prepare the PR.

I need:
- A PR title following the [ADO-12303] convention
- A PR description that mentions Story: A3 and Work-Item: ADO-12303
- A summary of what changed for the reviewer
```

### Post-merge sync

```
Story A3 merged. Please:
1. Update the trackerId in story A3 to ADO-12303 (it's already there —
   confirm lastSync is current)
2. Update the Azure DevOps work item state to Done
3. Update tasks.md to mark A3 complete in the Sprint 2 checklist
```

### Noticing a deviation from the design

```
During implementation of A3 I made a decision that differs from design.md.

DEC-003 said "middleware-based auth via FastAPI Depends". But I implemented
require_role as a dependency factory (a function that returns a Depends),
not a class-based middleware. It achieves the same goal but the shape differs.

Should this be recorded as a deviation? If yes, help me:
1. Add it to deviations_from_design in work-item-map.yaml
2. Create an ADR at docs/decisions/0003-rbac-depends-pattern.md
```

---

## Phase 7: End-of-Sprint and Sync

### End-of-sprint sync

```
Sprint 2 is done. Please sync all completed stories for Feature 101.

Attach: #work-item-sync-playbook

Stories to sync: A3 (just finished), A1 and A2 (synced previously — verify
their state is still current).

Show me the full payload before calling any write API.
```

### Drift check

```
Check for drift between our Azure DevOps tracker and the story files
for Feature 101. Someone may have updated effort or sprint assignment
in ADO directly.

Show me any field that differs since lastSync.
```

### PI retrospective

```
PI 1 is closing. Help me:

1. List all stories that are Done vs still open
2. For open stories, note their current state and whether they're blocked
3. Draft the rollover — which stories move to PI 2 and which are cancelled
4. Update deferred_to_next_pi in work-item-map.yaml for Feature 101 and 301
5. Summarize the deviations (DEV-001 through DEV-00N) we accumulated this PI

I'll review and approve each change before you write anything.
```

---

## Steering File Management

### Adding context mid-project

```
We made a new architectural decision today: all database migrations will use
Alembic with a single-tenant migration runner that iterates over tenant schemas.

Please update technology-guidelines.md to add this constraint so future
sessions know about it.
```

### Updating the product overview after a PI

```
PI 1 shipped. Update product-overview.md to reflect:
- Epic 1 Feature 101 (Auth): DONE
- Epic 3 Feature 301 (Terraform foundation): partially done — I1 done, I2–I4 carry over
- Revised NFRs: we validated <200ms P99 auth latency in load testing
```

### Recovering context after a break

```
I'm picking this project back up after two weeks away.

Read product-overview.md, the current tasks.md for Feature 101, and
the README for example-1-saas-platform. Then tell me:

1. Where did we leave off?
2. What's in progress?
3. What should I work on next?
```

---

## Quick Reference: Prompts by Phase

| Phase | Situation | Prompt starter |
|-------|-----------|---------------|
| PRD Intake | First session | `"Here's our PRD. Help me break it into epics..."` |
| PRD Intake | Create steering | `"Based on our discussion, create product-overview.md and technology-guidelines.md"` |
| Feature | Decompose epic | `"Decompose Epic N into features for PI 1. Team: X, capacity: Y..."` |
| Feature | Create folder | `"Create the spec folder for Feature NNN. From our discussion:..."` |
| Story | Create stories | `"Create stories for Feature NNN. Team context:..."` |
| Story | Refine AC | `"This acceptance criterion is too vague. Help me make it specific:..."` |
| Story | Sync to tracker | `"Create all Feature NNN stories in ADO. Show me the payload first."` |
| Planning | Add impl tasks | `"I'm planning story X. Here's my approach: [1, 2, 3]. What am I missing?"` |
| Implementation | Start story | `"I'm starting story X (ADO-NNNNN). Let's execute task 1."` |
| Implementation | Record deviation | `"I made a decision that differs from design.md. Should this be a deviation?"` |
| Review | Prepare PR | `"Story X is done. Help me prepare the PR."` |
| Sync | End of sprint | `"Sprint N is done. Sync all Done stories for Feature NNN."` |
| Sync | Drift check | `"Check for drift between the tracker and our story files."` |
| Context | After a break | `"Read these files and tell me where we left off and what's next."` |
