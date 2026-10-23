---
inclusion: manual
---

# Onboarding Guide

Attach with `#onboarding-guide` in your first sessions. Ask Kiro to walk you through any section.

## Day One Setup

| Step | Command or action |
|------|------------------|
| 1. Clone | `git clone [REPO-URL]` |
| 2. Toolchain | Install [LANGUAGE] [VERSION], [PACKAGE-MANAGER], Terraform [TERRAFORM-VERSION], AWS CLI v2 |
| 3. Dependencies | `[INSTALL-COMMAND]` |
| 4. Pre-commit | `[PRE-COMMIT-INSTALL-COMMAND]` |
| 5. Cloud access | Request [ACCESS-ROLE] via [ACCESS-REQUEST-PROCESS], then `[SSO-LOGIN-COMMAND]`. Never create long-lived access keys — all access runs through [ACCESS-MECHANISM]. |
| 6. Verify | `[TEST-COMMAND]` passes locally before you change anything |

## Read the Steering Files First

`.kiro/steering/` holds the rules Kiro applies to every session. Read them in this order — you will absorb the project faster here than from source:

1. `product-overview.md` — what we build and for whom
2. `technology-guidelines.md` — the mandated stack and why
3. `repository-structure.md` — where code goes
4. `coding-standards.md` — how we write it
5. `domain-glossary.md` — the vocabulary; use these exact words
6. `security-guidelines.md` — the non-negotiables

Flag anything unclear or stale in your first week. Outdated steering makes Kiro produce outdated code, so fixing it is real work, not housekeeping.

## How to Read a Spec

Each feature is a folder under `.kiro/specs/[FEATURE-ID]-[FEATURE-SLUG]/`:

| File | What it answers |
|------|----------------|
| `requirements.md` | What must be true, as acceptance criteria |
| `design.md` | How we decided to build it, and the alternatives rejected |
| `tasks.md` | Feature-level checklist across stories |
| `stories/` | One file per story, the unit you actually pick up |
| `work-item-map.yaml` | Story-to-tracker mapping and recorded deviations from design |

Read `requirements.md` then `design.md` before touching a story. A story assumes both.

## Picking Up a Story

1. Find your story in `.kiro/specs/<feature>/stories/`, named `[REF]-[TRACKER-ID]-[SLUG].md`.
2. Tell Kiro: *"I'm starting story [REF]. Let's discuss the approach."* Discuss before code — that conversation is where design mismatches surface cheaply.
3. Kiro adds an Implementation Tasks section to the story file, then works through it. You review each step.
4. Set `state: Active` in the story front matter via Kiro. Never hand-edit the YAML.
5. Branch, commit, and open the PR per `#pr-conventions`.
6. Sync state to the tracker per `#work-item-sync-playbook`.

## Quality Gates

- Hooks in `.kiro/hooks/` run automatically: lint on save, secret guard before writes, tests after each task, spec consistency checks. If a hook blocks you, fix the cause rather than disabling the hook.
- CI enforces lint, types, tests at [COVERAGE-PERCENT]% coverage, security scan at [SEVERITY-THRESHOLD], and Terraform validation.
- A story is done when every task is checked, every acceptance criterion has a test, and deviations are recorded in `work-item-map.yaml`.

## Who to Ask

| Topic | Contact |
|-------|---------|
| Product and priorities | [PRODUCT-OWNER-ALIAS] |
| Architecture | [TECH-LEAD-ALIAS] |
| Cloud access | [PLATFORM-CONTACT-ALIAS] |
| Anything in this repo | Ask Kiro first — it has the steering and specs loaded |
