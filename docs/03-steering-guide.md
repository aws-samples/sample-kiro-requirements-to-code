# Steering Files Guide

## What Are Steering Files?

Steering files provide Kiro with **persistent context** about your project. They are Markdown documents that encode your product vision, technology constraints, coding standards, and operational procedures — so Kiro never "forgets" your conventions between sessions.

Think of steering files as your project's institutional knowledge, written in a format an AI development partner can consume and apply consistently.

---

## Why Steering Files Matter

| Without Steering | With Steering |
|-----------------|---------------|
| Kiro asks "what cloud provider?" every session | Kiro knows it's AWS and applies AWS-native patterns |
| Code style varies based on conversation context | Consistent naming, structure, and patterns every time |
| New team members get inconsistent guidance | Everyone (including Kiro) follows the same standards |
| Context is rebuilt from scratch each conversation | Kiro starts with full project understanding |

---

## Inclusion Types

Steering files have three inclusion modes, controlled by front-matter:

### Always (Default)

```yaml
---
inclusion: always
---
```

Loaded into **every** Kiro conversation automatically. Use for:
- Product overview and architecture
- Technology constraints
- Repository structure
- Coding standards
- Work-item conventions

**Guideline:** Keep always-included files concise. Total always-loaded content should ideally stay under 3000 words combined. Focus on constraints and decisions, not tutorials.

### File Match (Conditional)

```yaml
---
inclusion: fileMatch
fileMatchPattern: "infra/**"
---
```

Loaded **only when** a file matching the pattern is read into context. Use for:
- Domain-specific standards (Terraform conventions when editing .tf files)
- Vertical-specific context (payment domain rules when editing payment code)
- Framework guidelines (React patterns when editing .tsx files)

**Guideline:** Use fileMatch for standards that only apply to a subset of your codebase. This keeps irrelevant context out of unrelated conversations.

### Manual

```yaml
---
inclusion: manual
---
```

Loaded **only when** explicitly referenced with `#filename` in chat. Use for:
- Action playbooks (sync protocol, deployment runbook)
- Reference material that's too large for always-include
- Situational procedures (incident response, release process)

**Guideline:** Use manual for procedural documents that guide multi-step workflows. The developer attaches them when they need to execute that procedure.

---

## Steering File Anatomy

```markdown
---
inclusion: always
---

# Title

## Section 1: Key Constraints
- Constraint A
- Constraint B

## Section 2: Conventions
| Convention | Rule |
|-----------|------|
| X | Do Y |

## Section 3: Patterns
When [situation], always [approach].
```

### Front-matter (required for fileMatch and manual)

```yaml
---
inclusion: fileMatch          # always | fileMatch | manual
fileMatchPattern: "src/**"    # glob pattern (fileMatch only)
---
```

If no front-matter is present, the file defaults to `always` inclusion.

---

## Recommended Steering File Set

### Minimal (Every Project)

| File | Inclusion | Content |
|------|-----------|---------|
| `product-overview.md` | always | Product vision, epics, architecture layers, key terminology |
| `technology-guidelines.md` | always | Cloud provider, languages, frameworks, OS, key constraints |
| `coding-standards.md` | always | Naming, file structure, testing, documentation standards |
| `repository-structure.md` | always | Folder layout, module boundaries, asset flow |

### Extended (Larger Projects)

All of these ship as ready-to-fill templates in [`templates/steering/`](../templates/steering/):

| File | Inclusion | Content |
|------|-----------|---------|
| `security-guidelines.md` | always | Secrets handling, authn/z defaults, dependency policy |
| `domain-glossary.md` | always | Ubiquitous language — terms, definitions, invariants |
| `infra-guidelines.md` | fileMatch: `infra/**` | Terraform, container, cloud service standards |
| `api-guidelines.md` | fileMatch: `src/api/**` | REST conventions, error handling, versioning |
| `testing-strategy.md` | fileMatch: `tests/**` | Test pyramid, coverage floors, mocking policy |
| `observability-guidelines.md` | fileMatch: `src/**` | Logging, tracing, metrics, correlation IDs |
| `work-item-sync-playbook.md` | manual | Bidirectional sync protocol with tracker |
| `pr-conventions.md` | manual | Branch names, commit format, PR sections, merge rules |
| `onboarding-guide.md` | manual | New-engineer reading path through steering and specs |

The fileMatch pattern extends naturally to domains this repository doesn't ship a
template for — a `frontend-guidelines.md` matched on `src/web/**` or a
`data-guidelines.md` matched on `src/data/**` follows the same shape.

---

## Writing Effective Steering Files

### Principles

1. **Be prescriptive, not descriptive** — "Use X" not "X is an option"
2. **Include the why** — "Use Cognito because we need HIPAA BAA" not just "Use Cognito"
3. **Be specific** — "Provider pin: `aws ~> 5.0`" not "Pin provider versions"
4. **Use tables for conventions** — Easy to scan, hard to misinterpret
5. **Keep it current** — Update when decisions change; stale steering is worse than no steering
6. **Cross-reference** — Use `#[[file:path]]` to include related documents by reference

### Anti-Patterns

| Anti-Pattern | Problem | Fix |
|-------------|---------|-----|
| 5000-word always-included file | Bloats every session's context | Split into always + fileMatch sections |
| Describing the tech stack without constraints | Kiro knows what .NET is; tell it YOUR rules | Focus on project-specific decisions |
| Contradicting your own conventions | Kiro gets confused, produces inconsistent code | Single source of truth per topic |
| Never updating after decisions change | Kiro applies outdated rules | Review steering after major ADRs |
| Duplicating IDE/linter config | Redundant; config files already enforce it | Reference the config, add the WHY |

### Template: Product Overview

```markdown
---
inclusion: always
---

# Product Overview

## Vision
[One paragraph: what the product does and for whom]

## Architecture Layers
1. **Infrastructure** — [what lives here]
2. **Platform Services** — [what lives here]
3. **Domain Services** — [what lives here]
4. **Application Layer** — [what lives here]

## Epics (Current Scope)
| Epic | Description | Status |
|------|-------------|--------|
| Epic 1 | ... | In Progress |
| Epic 2 | ... | Planned |

## Key Terminology
| Term | Definition |
|------|-----------|
| [Term] | [What it means in this project] |

## Non-Functional Requirements
- Security: [key requirement]
- Scalability: [key requirement]
- Compliance: [key requirement]
```

### Template: Technology Guidelines

```markdown
---
inclusion: always
---

# Technology Guidelines

## Mandated Technologies
| Component | Technology | Rationale |
|-----------|-----------|-----------|
| Cloud | AWS | [why] |
| Language | [lang] | [why] |
| Framework | [framework] | [why] |
| Database | [db] | [why] |
| IaC | Terraform | [why] |

## Constraints
- All new code must target Linux
- [Other hard constraint]
- [Other hard constraint]

## Compatibility Matrix
| Component | Current | Target | Flexibility |
|-----------|---------|--------|-------------|
| ... | ... | ... | High/Medium/Low |
```

### Template: Infrastructure Guidelines

```markdown
---
inclusion: fileMatch
fileMatchPattern: "infra/**"
---

# Infrastructure Standards

## Terraform
- [Module layout rule]
- [State management rule]
- [Provider pinning rule]
- [Quality gate rule]

## Containers
- [Base image rule]
- [Security rule]
- [Health check rule]

## AWS Baseline
- [Encryption rule]
- [Networking rule]
- [IAM rule]
```

---

## File References

Steering files can reference other documents using the `#[[file:path]]` syntax:

```markdown
For the full API specification, see:
#[[file:docs/openapi.yaml]]

For the database schema:
#[[file:docs/schema.sql]]
```

This pulls the referenced document into Kiro's context when the steering file is loaded. Use it for:
- API specifications (OpenAPI, GraphQL schema)
- Database schemas
- Architecture diagrams (in Mermaid)
- Compliance checklists

**Caution:** Referenced files add to context size. Keep references focused on documents that influence implementation decisions.

---

## Evolving Steering Over Time

### When to Update Steering

| Event | Action |
|-------|--------|
| New architectural decision (ADR) | Update relevant steering file with the decision |
| Technology change | Update technology-guidelines.md |
| New team convention agreed | Add to coding-standards.md |
| New epic starts | Update product-overview.md |
| New domain area begins | Create new fileMatch steering file |
| Convention proves wrong | Remove or revise — don't leave contradictions |

### Review Cadence

- **Every PI boundary** — Review product-overview.md and technology-guidelines.md
- **After major ADRs** — Update the relevant steering file immediately
- **Onboarding new engineer** — Ask them to read steering files and flag what's unclear or outdated
