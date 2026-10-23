# Plan: Kiro Spec-Driven Development — AWS Samples Reference

**Status:** v1 shipped — this plan is reconciled against what was actually built; remaining items are marked *Roadmap*
**Author:** Mitesh/Anand / Kiro
**Date:** 2026-07-02 · **Last reconciled:** 2026-08-25

> **How to read this document.** Sections 1–5 describe the methodology and are current.
> Sections 6–13 were written as a forward plan; they have been updated to reflect the
> shipped v1 content, with deferred items explicitly labelled *Roadmap* rather than
> silently left as if they existed. Where the shipped shape deliberately differs from
> the original plan (e.g., workflow template names), the delta is noted inline.

---

## 1. Purpose

Publish a comprehensive reference repository demonstrating how to use Kiro's spec-driven development workflow end-to-end. The repository will serve as the go-to guide for AWS customers adopting Kiro for structured software delivery.

**Key value proposition:** Show how a Product Requirements Document becomes shipped, reviewed, validated code through a repeatable, traceable process — with Kiro as the AI development partner at every stage.

---

## 2. Target Audience

- Engineering teams evaluating or adopting Kiro
- Technical leads wanting a structured development methodology
- Teams with existing work-item trackers (Azure DevOps, GitHub Issues, Jira) who want bidirectional sync
- Platform teams building on AWS who want proven patterns for specs, steering, hooks, and team workflows

---

## 3. Repository Name

**Decision:** `kiro-prd-to-code`

Named for the journey the reference teaches — a Product Requirements Document becoming
shipped code. Kiro's own term for the methodology, *spec-driven development*, stays in
the repository description and README tagline so adopters searching Kiro's vocabulary
still find it.

---

## 4. Core Narrative: The Complete Journey

The repository demonstrates this complete flow:

```
┌────────────────────────────────────────────────────────────────────────────┐
│  1. PRODUCT REQUIREMENTS DOCUMENT (PRD)                                    │
│     Rich document: vision, user journeys, NFRs, constraints, success       │
│     criteria. Written by Product Owner.                                    │
└──────────────────────────────────┬─────────────────────────────────────────┘
                                   │ Developer + Kiro conversation:
                                   │ "Here's our PRD. Help me decompose."
                                   ▼
┌────────────────────────────────────────────────────────────────────────────┐
│  2. EPICS (Major Capability Areas)                                         │
│     Kiro produces:                                                         │
│     - steering/product-overview.md (always-loaded context)                 │
│     - specs/epic-N-<name>/README.md per epic                               │
│     - Dependency map between epics                                         │
└──────────────────────────────────┬─────────────────────────────────────────┘
                                   │ "Decompose Epic 1 into features for PI 1."
                                   ▼
┌────────────────────────────────────────────────────────────────────────────┐
│  3. FEATURES (Deliverable Increments — completable in one PI)              │
│     Kiro creates per feature:                                              │
│     - requirements.md (traceability to PRD)                                │
│     - design.md (architectural decisions, DEC-NNN format)                  │
│     - tasks.md (sprint-organized checklist)                                │
│     - work-item-map.yaml (index, capacity, deviations)                     │
└──────────────────────────────────┬─────────────────────────────────────────┘
                                   │ "Create stories for Feature 101."
                                   ▼
┌────────────────────────────────────────────────────────────────────────────┐
│  4. STORIES (Implementable Units — 1-5 person-days)                        │
│     Each story file has:                                                   │
│     - YAML front-matter (scheduling, ownership, effort, tags)              │
│     - Context, Goal, Scope, Out of Scope                                   │
│     - Acceptance Criteria (Given/When/Then)                                │
│     - Dependencies                                                         │
└──────────────────────────────────┬─────────────────────────────────────────┘
                                   │ "I'm starting story A1. Let's discuss
                                   │  the implementation approach."
                                   ▼
┌────────────────────────────────────────────────────────────────────────────┐
│  5. IMPLEMENTATION TASKS (Subtasks within a story)                         │
│     Added AFTER discussing approach with Kiro:                             │
│     - Grouped by logical theme (e.g., "Task 1: Database Layer")            │
│     - Checkboxes tracked as work progresses                                │
│     - Final task group is always "Validation"                              │
└──────────────────────────────────┬─────────────────────────────────────────┘
                                   │ Kiro writes code, checks boxes,
                                   │ runs validation gates
                                   ▼
┌────────────────────────────────────────────────────────────────────────────┐
│  6. DELIVERED CODE + PR + REVIEW + MERGE + SYNC                            │
│     - Branch: story/<id>-<slug>                                            │
│     - PR reviewed by team + automated completeness check                   │
│     - CI validates quality gates                                           │
│     - Merge → CD deploys                                                   │
│     - Story state synced to tracker                                        │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## 5. Team Workflows

### 5.1 Sprint Planning Workflow

```
┌──────────────────────────────────────────────────────────────────────────┐
│  SPRINT PLANNING                                                         │
│                                                                          │
│  1. Team reviews upcoming stories in tasks.md                            │
│  2. Developers discuss approach with Kiro per story                      │
│  3. Kiro adds ## Implementation Tasks to each story file                 │
│  4. Developer raises a SPEC PR:                                          │
│     - Branch: spec/<feature-slug>                                        │
│     - Changes: story files with impl tasks added                         │
│     - Reviewers: tech lead + peer                                        │
│  5. Team reviews the plan (impl tasks, effort, dependencies)             │
│  6. On approval + merge: sprint is baselined                             │
│                                                                          │
│  PR title: [SPEC] Feature 101 — Sprint 2 implementation plans            │
│  PR content: Story files with ## Implementation Tasks sections           │
└──────────────────────────────────────────────────────────────────────────┘
```

**What gets reviewed in a Spec PR:**
- Are implementation tasks comprehensive?
- Is the approach aligned with the design.md decisions?
- Are there missing validation tasks?
- Are dependencies correctly identified?
- Is effort realistic given the task breakdown?

### 5.2 Implementation PR Workflow

```
┌──────────────────────────────────────────────────────────────────────────┐
│  IMPLEMENTATION PR                                                       │
│                                                                          │
│  1. Developer implements story (Kiro writes code, checks tasks)          │
│  2. Developer raises an IMPLEMENTATION PR:                               │
│     - Branch: story/<tracker-id>-<slug>                                  │
│     - Contains: code, infra, docs, ADRs                                  │
│     - Commit trailer: Work-Item: <tracker-id>                            │
│  3. CI runs automated checks:                                            │
│     - Lint, build, test, security scan                                   │
│     - Terraform plan (if infra/)                                         │
│     - Work-item link validation                                          │
│  4. Automated completeness review (PR workflow):                         │
│     - Are all implementation tasks checked off?                          │
│     - Are all acceptance criteria addressed?                             │
│     - Are there any gaps between story scope and delivered code?         │
│     - Are validation tasks (fmt, lint, test) passing?                    │
│  5. Human reviewer approves                                              │
│  6. Merge → CD deploys → Sync state to tracker                           │
│                                                                          │
│  PR title: [<tracker-id>] Short summary of implementation                │
└──────────────────────────────────────────────────────────────────────────┘
```

### 5.3 Automated PR Completeness Review

Shipped as `templates/workflows/pr-completeness-review.template.yml` — a GitHub Action
that runs on every `story/*` pull request:

```
┌───────────────────────────────────────────────────────────────────────────┐
│  PR COMPLETENESS REVIEW                                                   │
│                                                                           │
│  Inputs:                                                                  │
│  - PR branch name (extract story ref and tracker ID)                      │
│  - Story file (read impl tasks and acceptance criteria)                   │
│  - PR diff (files changed)                                                │
│                                                                           │
│  Checks:                                                                  │
│  ┌─────────────────────────────────────────────────────────────────┐      │
│  │ ✅ All implementation task checkboxes are [x]                   │      │
│  │ ✅ Validation task boxes checked (lint, format, test, security) │      │
│  │ ✅ Files created match scope described in story                 │      │
│  │ ✅ No obvious gaps (acceptance criteria → code coverage)        │      │
│  │ ✅ Work-item ref in the PR title, body, or branch               │      │
│  │ ✅ ADR created if story makes architectural decisions           │      │
│  │ ⚠️  Warnings for unchecked optional items                       │      │
│  └─────────────────────────────────────────────────────────────────┘      │
│                                                                           │
│  Output:                                                                  │
│  - PR comment with a completeness report (advisory)                       │
│  - Merge blocking comes from the required checks, not this                │
│    comment: spec-integrity, work-item-link-check, code-quality            │
└───────────────────────────────────────────────────────────────────────────┘
```

### 5.4 Sprint Retrospective / Sync Workflow

```
┌──────────────────────────────────────────────────────────────────────────┐
│  END-OF-SPRINT SYNC                                                      │
│                                                                          │
│  1. Developer attaches #work-item-sync-playbook                          │
│  2. "Sync all completed stories to the tracker"                          │
│  3. Kiro reads tracker state, computes diffs                             │
│  4. Developer approves state transitions                                 │
│  5. Kiro updates tracker (Done, remaining effort)                        │
│  6. "Check for drift" — detect if tracker was edited directly            │
│  7. Record deviations in work-item-map.yaml                              │
│  8. Update tasks.md checkboxes for completed stories                     │
│                                                                          │
│  Produces: Updated work-item-map, synced tracker, deviation log          │
└──────────────────────────────────────────────────────────────────────────┘
```

### 5.5 Feature Onboarding Workflow (Pull from Tracker)

```
┌──────────────────────────────────────────────────────────────────────────┐
│  ONBOARDING A NEW FEATURE FROM TRACKER                                   │
│                                                                          │
│  Prompt: "Pull Feature <ID> from the tracker into Kiro specs"            │
│                                                                          │
│  1. Kiro reads the Feature work item + all child Stories                 │
│  2. Creates the spec folder structure                                    │
│  3. Generates requirements.md from Feature description                   │
│  4. Generates story files from child Story work items                    │
│  5. Populates work-item-map.yaml                                         │
│  6. Sets lastSync timestamps                                             │
│                                                                          │
│  Use when: Team has existing work in tracker and wants to adopt Kiro     │
└──────────────────────────────────────────────────────────────────────────┘
```

### 5.6 Real-World Scenarios (Roadmap — planned guides 10 and 11)

The documentation will cover these common situations that deviate from the happy path:

| Scenario | How It's Handled |
|----------|-----------------|
| Mid-sprint scope change | Process for adding/removing stories mid-sprint, re-planning with Kiro |
| Cross-team dependencies | Blocked-by tracking in story front-matter, coordination patterns |
| Technical debt tracking | Capture debt during implementation, backlog grooming pattern |
| Hotfix / emergency workflow | Bypass spec flow for production issues, reconcile after |
| Multi-repo coordination | How steering and specs work across repositories |
| PI boundary transitions | Roll forward incomplete work, update sprint aliases, refresh steering |
| Feature flagging | Stories that ship behind flags, state tracking for partial delivery |
| Onboarding existing project | Step-by-step brownfield adoption of the methodology |

---

## 6. Repository Structure (as shipped in v1)

```
kiro-prd-to-code/
├── README.md                              # Overview, architecture diagram, quick start
├── LICENSE                                # MIT-0
├── CONTRIBUTING.md
├── CODE_OF_CONDUCT.md
│                                                                          │
├── docs/                                  # Methodology documentation (6 shipped, 5 roadmap — see §9)
│   ├── 01-process-guide.md               # Full lifecycle (five phases)
│   ├── 02-prd-decomposition-guide.md     # PRD → Epics → Features → Stories → Tasks
│   ├── 03-steering-guide.md              # Writing effective steering files
│   ├── 04-hooks-guide.md                 # Automating quality gates (v1 hook schema)
│   ├── 05-work-item-sync-guide.md        # Bidirectional tracker sync
│   └── 06-getting-started.md             # Setup tutorial + first conversation scripts
│                                                                          │
├── templates/                             # Generic copy-paste starters
│   ├── steering/                          # 13 steering file templates
│   ├── specs/                             # 5 spec file templates (see §7.2)
│   ├── hooks/                             # 10 hook templates + 4 shared scripts
│   └── workflows/                         # 6 GitHub Actions templates + adoption README
│                                                                          │
├── examples/
│   ├── example-1-saas-platform/           # Full worked example: container-based
│   │   ├── sample-prd/
│   │   │   └── product-requirements.md    # Rich PRD
│   │   ├── .kiro/
│   │   │   ├── steering/                  # 5 steering files
│   │   │   ├── hooks/                     # 6 hooks + scripts
│   │   │   ├── specs/                     # 2 epic READMEs, 2 features, 8 stories
│   │   │   └── settings/mcp.json
│   │   ├── docs/decisions/                # ADRs (story deliverables)
│   │   ├── infra/                         # Terraform: bootstrap + root + Cognito module
│   │   ├── src/                           # FastAPI auth package (story A2 output)
│   │   └── tests/                         # Unit tests for the auth package
│                                                                          │
│   └── example-2-data-pipeline/           # Full worked example: serverless
│       ├── sample-prd/
│       │   └── product-requirements.md    # Rich PRD
│       ├── .kiro/
│       │   ├── steering/                  # 4 steering files
│       │   ├── hooks/                     # 5 hooks + scripts
│       │   ├── specs/                     # 1 epic README, 1 feature, 4 stories
│       │   └── settings/mcp.json
│       ├── infra/                         # Terraform: root + ingestion module
│       ├── src/                           # Lambda handler + shared layer (story E1 output)
│       └── tests/                         # Unit tests for handler and layer
```

**Deltas from the original plan:**
- Examples do **not** vendor `.github/workflows/`; CI/CD ships once as `templates/workflows/`
  (six ready-to-adopt workflows), which avoids duplicating ~1,600 lines of YAML per example.
- The planned `cli/` folder was not built. Its purpose — the automated PR completeness
  check — shipped instead as `templates/workflows/pr-completeness-review.template.yml`
  plus the stdlib Python checkers in `templates/hooks/scripts/`.

---

## 7. Template Inventory

### 7.1 Steering Templates (13 total)

| # | Template | Inclusion | Priority |
|---|----------|-----------|----------|
| 1 | `product-overview.template.md` | always | Must have |
| 2 | `technology-guidelines.template.md` | always | Must have |
| 3 | `coding-standards.template.md` | always | Must have |
| 4 | `repository-structure.template.md` | always | Must have |
| 5 | `infra-guidelines.template.md` | fileMatch | Must have |
| 6 | `work-item-sync-playbook.template.md` | manual | Must have |
| 7 | `security-guidelines.template.md` | always | Should have |
| 8 | `api-guidelines.template.md` | fileMatch | Should have |
| 9 | `testing-strategy.template.md` | fileMatch | Should have |
| 10 | `observability-guidelines.template.md` | fileMatch | Should have |
| 11 | `domain-glossary.template.md` | always | Nice to have |
| 12 | `pr-conventions.template.md` | manual | Nice to have |
| 13 | `onboarding-guide.template.md` | manual | Nice to have |

### 7.2 Spec Templates (5 shipped)

| # | Template | Purpose |
|---|----------|---------|
| 1 | `story-template.md` | Canonical story file format |
| 2 | `requirements.template.md` | Feature requirements with PRD traceability |
| 3 | `design.template.md` | Architectural decisions (DEC-NNN format) |
| 4 | `tasks.template.md` | Sprint-organized checklist |
| 5 | `work-item-map.template.yaml` | Feature index, capacity, deviations |

The planned `epic-readme.template.md` was folded into the guides instead: the epic README
format is documented in `docs/02-prd-decomposition-guide.md` (§Step 2), and both examples
ship real epic READMEs to copy from.

### 7.3 Hook Templates (10 shipped)

All hooks use the v1 JSON schema (`{"version": "v1", "hooks": [...]}`) with PascalCase
trigger names — see `docs/04-hooks-guide.md` for the full field reference. The original
plan predated the v1 schema and listed camelCase events (`postToolUse`, `fileEdited`) and
a `.template.hook` extension; both are obsolete.

| # | Template | Trigger | Action | Priority |
|---|----------|---------|--------|----------|
| 1 | `terraform-validate.template.json` | PostFileSave | agent | Must have |
| 2 | `design-review.template.json` | PostFileCreate | agent | Must have |
| 3 | `lint-on-save.template.json` | PostFileSave | command | Must have |
| 4 | `test-after-task.template.json` | PostTaskExec | command | Must have |
| 5 | `spec-consistency.template.json` | PostFileSave | agent | Must have |
| 6 | `secret-guard.template.json` | PreToolUse (blocking) | command | Must have |
| 7 | `security-scan.template.json` | PostFileSave | command | Should have |
| 8 | `session-context.template.json` | SessionStart | command | Should have |
| 9 | `api-contract-check.template.json` | PostFileSave | agent | Nice to have |
| 10 | `dependency-audit.template.json` | PostFileSave | agent | Nice to have |

The planned `commit-message-check` and `pre-task-context` hooks were replaced by
`secret-guard` (a real blocking guard rail) and `session-context` (session priming),
which proved more broadly useful. Shared logic lives in `templates/hooks/scripts/`
(4 stdlib-only Python scripts reused by hooks and CI).

### 7.4 Workflow Templates (6 shipped)

| # | Template | Trigger | Priority |
|---|----------|---------|----------|
| 1 | `spec-integrity.template.yml` | PR (.kiro/**), push to main | Must have |
| 2 | `work-item-link-check.template.yml` | All PRs | Must have |
| 3 | `code-quality.template.yml` | PR (src/tests) | Must have |
| 4 | `terraform-plan.template.yml` | PR (infra/) | Must have |
| 5 | `terraform-apply.template.yml` | Merge (infra/) | Must have |
| 6 | `pr-completeness-review.template.yml` | PR (story/* branch) | Should have |

Names differ from the original plan because the shape settled differently during build:
`spec-integrity` replaced `spec-pr-review` with a real checker script instead of a review
prompt, `pr-completeness-review` merged `implementation-pr-review` and
`kiro-completeness-check` (they produced the same comment), and `code-quality` covers the
language gates that had no template at all. `templates/workflows/README.md` documents
this mapping and the adoption order.

---

## 8. MCP Server Coverage

### Primary (configured in the examples, documented in guide 05)

| MCP Server | Use Case | Where |
|-----------|----------|-------|
| Azure DevOps | Enterprise work-item sync (create, update, drift detection) | Example 1 `mcp.json` (ships disabled until a PAT is set) |
| GitHub | Lightweight issue sync + PR management | Both examples' `mcp.json` (ships disabled until a token is set) |
| AWS Docs | Documentation search during implementation | Both examples' `mcp.json`, enabled |

### Extensibility (add-it-yourself candidates)

| MCP Server | Use Case |
|-----------|----------|
| AWS Pricing | Cost estimation during the design phase |
| Jira (community) | Bidirectional sync for Jira-based teams |
| Confluence (community) | Pull existing design docs into specs |
| Slack/Teams notification | Post sprint sync summaries to team channel |
| SonarQube / CodeQL | Security and quality metrics in PR review |

---

## 9. Documentation

### Shipped (6 guides)

| # | Document | Key Sections |
|---|----------|-------------|
| 1 | `01-process-guide.md` | Five phases, roles, quality gates, story lifecycle, anti-patterns |
| 2 | `02-prd-decomposition-guide.md` | PRD analysis, epic extraction, feature decomposition, story creation, implementation task patterns (infra-first, vertical-slice, spike-then-implement, foundation-then-extend) |
| 3 | `03-steering-guide.md` | Inclusion types, writing principles, recommended steering set, file references, evolution cadence |
| 4 | `04-hooks-guide.md` | v1 hook schema field reference, all 10 triggers, command vs agent actions, exit-code semantics, all 10 shipped hooks, design patterns (guard rails, post-write validation, session priming, verify-then-continue) |
| 5 | `05-work-item-sync-guide.md` | Source-of-truth model, ADO setup, GitHub setup, create/update/pull flows, aliases, field mappings |
| 6 | `06-getting-started.md` | Prerequisites, quick setup, MCP config, first conversation scripts, verify checklist |

Team workflow and PR-review content originally planned as separate guides 06/07 shipped
inside `templates/workflows/README.md` (adoption order, required checks, OIDC setup) and
§5 of this plan; conversation patterns are embedded in guides 02 and 06.

### Roadmap (5 guides)

| # | Document | Key Sections |
|---|----------|-------------|
| 7 | `07-team-workflows.md` | Sprint planning PR, implementation PR, retrospective sync, feature onboarding from tracker (expand §5 of this plan into a guide) |
| 8 | `08-pr-review-automation.md` | How the completeness workflow works, PR comment format, merge blocking rules |
| 9 | `09-conversation-patterns.md` | What to say to Kiro at each phase — real prompt examples for decomposition, planning, implementation, review, sync |
| 10 | `10-scaling-and-adoption.md` | Onboarding existing (brownfield) projects, scaling to larger teams, mapping to Scrum/SAFe/Kanban ceremonies, metrics for measuring success |
| 11 | `11-failure-recovery.md` | Wrong specs, sync conflicts, rollback patterns, mid-sprint scope changes, hotfix reconciliation, PI boundary transitions |

---

## 10. Examples: What They Demonstrate

### Example 1: SaaS Platform ("TaskFlow") — as shipped

| Aspect | Detail |
|--------|--------|
| **Domain** | Multi-tenant project management SaaS |
| **Stack** | Python 3.12 / FastAPI / ECS Fargate / Aurora Serverless v2 / Cognito |
| **Tracker shown** | Azure DevOps (enterprise ADO MCP sync) |
| **PRD** | Rich — vision, personas, 4 epics, NFRs, constraints, delivery timeline, success criteria |
| **Decomposition** | 4 epics in PRD → 2 epic READMEs → 2 features fully decomposed → 8 stories |
| **Features fully decomposed** | Authentication (A1–A4), Terraform Foundation (I1–I4) |
| **Stories with impl tasks** | 3 completed (A1, A2, I1) showing full task execution; A2's code and tests ship in `src/` and `tests/` |
| **Workflows shown** | Tracker sync playbook; CI/CD via `templates/workflows/` |
| **Hooks** | Terraform validate, design review, Python lint, secret guard, spec consistency, session context |
| **Key patterns** | Multi-tenancy, RBAC, design decisions with rollback, deviation tracking (DEV-001), ADRs (`docs/decisions/`) |

### Example 2: Data Pipeline ("StreamProcess") — as shipped

| Aspect | Detail |
|--------|--------|
| **Domain** | Real-time event processing platform |
| **Stack** | Python 3.12 / Lambda + Powertools / Kinesis / API Gateway / S3 (Step Functions processing in Feature 201) |
| **Tracker shown** | GitHub Issues (lightweight sync) |
| **PRD** | Rich — vision, personas, 4 epics, NFRs, SLAs, schema standards, delivery timeline |
| **Decomposition** | 4 epics in PRD → 1 epic README → 1 feature fully decomposed → 4 stories |
| **Features fully decomposed** | REST API Ingestion (E1–E4) |
| **Stories with impl tasks** | 2 completed (E1, E4) showing Lambda and Terraform patterns; E1's handler and tests ship in `src/` and `tests/` |
| **Workflows shown** | GitHub Issues sync; CI/CD via `templates/workflows/` |
| **Hooks** | Lambda convention check, Terraform validate, Python lint, secret guard, spec consistency |
| **Key patterns** | Serverless decisions, DLQ patterns, event schemas, deviation tracking, pipeline config-as-code |

### Why Two Examples?

| Dimension | Example 1 | Example 2 |
|-----------|-----------|-----------|
| Architecture | Containers + relational DB | Serverless + event streams |
| Compute | ECS Fargate | Lambda |
| Multi-tenancy | Schema-per-tenant | Pipeline-per-source |
| Tracker | Azure DevOps (enterprise) | GitHub Issues (lightweight) |
| Complexity | Higher (stateful, RBAC, DB) | Medium (stateless, event-driven) |
| Team process | Full ADO sync playbook + capacity planning | Lighter GitHub flow |
| Decomposition depth | 2 features / 8 stories / 3 done | 1 feature / 4 stories / 2 done |

Shows the methodology is **architecture-agnostic** — same workflow, different stacks.

---

## 11. PRD Depth

Each example's PRD is a comprehensive document containing:

- Executive summary
- Product vision (1 paragraph)
- Target users / personas (table with needs)
- Epics with capability lists
- Non-functional requirements (detailed: security, scalability, availability, observability/performance)
- Technology constraints (table with rationale)
- Delivery timeline (PI-level scope)
- Success criteria (measurable, checkboxable)

This mimics what a real product owner would hand to an engineering team. Sections a
fuller PRD would add — step-by-step user journeys, an assumptions-and-risks register,
and a glossary — were left out to keep the examples readable; the decomposition guide
(`docs/02`) still covers how to mine those sections when your PRD has them.

---

## 12. Implementation Code Depth

**Decision: real code for completed stories, nothing speculative beyond them.**

- Enough to show that hooks fire against real files
- Enough to show the CI workflows have something to validate
- Completed stories ship their genuine output (code + tests); planned stories ship no code
- NOT full working applications — the products themselves are illustrative

For each example:
- `infra/`: real Terraform that passes `fmt`/`validate`/`tflint` (state bootstrap and/or one domain module)
- `src/` + `tests/`: the completed stories' actual output — small but real, runnable code rather than placeholder files
- CI/CD: provided once as `templates/workflows/` (working YAML for plan, apply, quality gates, and PR review) rather than duplicated per example

*The original plan said "minimal skeletons only"; the shipped depth deliberately exceeds
that for completed stories (A2 and E1 ship working, tested implementations) — a Done
story with fake code behind it would undermine the traceability message.*

---

## 13. Execution Phases

| Phase | Deliverables | Status |
|-------|-------------|--------|
| **Phase 1: Foundation** | README, docs 01–06, CONTRIBUTING, LICENSE | ✅ Done (guides 07–11 are roadmap, §9) |
| **Phase 2: Templates** | 13 steering, 5 specs, 10 hooks + 4 scripts, 6 workflows | ✅ Done |
| **Phase 3: Example 1 PRD + Specs** | Rich PRD, full .kiro/ setup (steering, hooks, specs with stories) | ✅ Done |
| **Phase 4: Example 1 Code** | Terraform (bootstrap, root, Cognito) + FastAPI auth package + tests + ADR | ✅ Done (CI/CD via shared templates) |
| **Phase 5: Example 2 PRD + Specs** | Rich PRD, full .kiro/ setup | ✅ Done |
| **Phase 6: Example 2 Code** | Terraform ingestion module + Lambda handler/layer + tests | ✅ Done (CI/CD via shared templates) |
| **Phase 7: Review Tooling** | Shipped as `pr-completeness-review` workflow + stdlib checker scripts (no separate `cli/`) | ✅ Done (shape changed) |
| **Phase 8: Polish** | Cross-links, Mermaid diagrams, roadmap guides 07–11 | 🔄 In progress |

---

## 14. Open Items

Resolved during the build:

- [x] Completed stories per example — settled at 3 in Ex1 (A1, A2, I1) and 2 in Ex2 (E1, E4)
- [x] ADR deliverables as story outputs — yes; Ex1 ships `docs/decisions/0001-jwt-library-choice.md`, recorded as deviation DEV-001 in the 101 work-item map
- [x] Completeness review mechanism — a GitHub Action (`pr-completeness-review.template.yml`); the same checker scripts also run as PostFileSave hooks locally
- [x] Jira — documented as MCP extensibility (§8) rather than a third worked example

Still open:

- [ ] Which roadmap guides (07–11) to prioritise for v1.1

---

## 15. Success Criteria

Checked items are verified against the v1 content; unchecked items await pilot-team
feedback or the roadmap guides (§9).

- [ ] A developer can clone the repo, read the getting-started guide, and set up Kiro for their project in < 30 minutes *(pilot feedback)*
- [ ] A tech lead can read the process guide and team workflows doc and adopt the methodology without external training *(pilot feedback; team-workflows guide is roadmap item 07)*
- [x] The PRD → code journey is fully traceable in each example (no gaps in the chain) — every requirement traces to a real PRD section, every completed story's claims verify against the shipped code, and `check-spec-integrity.py` passes with zero errors on both examples
- [x] Both examples work with different stacks and trackers, proving the approach is generic — FastAPI/ECS/ADO vs Lambda/Kinesis/GitHub Issues
- [x] Templates are immediately copy-paste usable with only placeholder replacement needed — all hook JSON and the work-item-map YAML parse as shipped; placeholders are greppable
- [ ] Team workflows (spec PR, impl PR, completeness review) are documented with enough detail to adopt directly *(§5 here + `templates/workflows/README.md` today; full guide is roadmap item 07)*
- [ ] Real-world scenarios (scope changes, hotfixes, brownfield adoption) are covered in documentation *(roadmap items 10–11)*

---

## Next Steps

1. **Circulate the shipped v1** — Gather feedback from pilot teams against the success criteria (§15)
2. **Prioritise roadmap guides** — Decide which of guides 07–11 (§9) land in v1.1; 07 (team workflows) and 11 (failure recovery) cover the most-asked questions
3. **Resolve remaining open items** (§14)
4. **Iterate on examples** — Extend Ex1 with Feature 302 (CI/CD adoption story) and Ex2 with Feature 201 (processing pipeline) as demand warrants

---

*This plan was produced collaboratively between the team and Kiro, using the spec-driven development methodology it describes.*
