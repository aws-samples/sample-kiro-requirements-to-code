# kiro-prd-to-code

A reference repository demonstrating how to use [Kiro](https://kiro.dev) for AI-assisted
spec-driven development — from a Product Requirements Document to shipped, reviewed,
validated code with end-to-end traceability at every step.

---

## What This Repository Teaches

Most teams treat AI coding assistants as autocomplete at scale. This repository shows a
different approach: using Kiro as a structured development partner throughout the entire
software delivery lifecycle, where every line of code can be traced back to a requirement
and every design decision is captured as a version-controlled artifact.

**The journey this repo demonstrates:**

```
Product Requirements Document
        │
        │  "Here's our PRD. Help me break it into epics."
        ▼
Epics  ──►  steering/product-overview.md
            .kiro/specs/epic-N-*/README.md
        │
        │  "Decompose Epic 1 into features for this PI."
        ▼
Features  ──►  requirements.md   (traceability to PRD)
               design.md         (architectural decisions, DEC-NNN format)
               tasks.md          (sprint checklist)
               work-item-map.yaml
        │
        │  "Create stories for Feature 101."
        ▼
Stories  ──►  YAML front-matter (owner, sprint, effort, state)
              Acceptance criteria (Given/When/Then)
              Dependencies
        │
        │  "I'm starting story A1. Let's discuss the approach."
        ▼
Implementation Tasks  ──►  Numbered, checkboxed subtasks added to story file
                           (always ending with a Validation task group)
        │
        │  Kiro writes code, checks boxes, runs validation
        ▼
Delivered Code  ──►  PR on story/<id>-<slug> branch
                     CI validates quality gates
                     Merge → tracker state synced
                     ADRs captured as story deliverables
                     Deviations logged in work-item-map.yaml
```

The result: a complete audit trail from PRD section → feature requirement → story →
design decision → implementation task → source file → test → ADR.

---

## Repository Structure

```
kiro-prd-to-code/
├── docs/                        # Methodology guides (6 shipped)
│   ├── 01-process-guide.md      # Full lifecycle, five phases, roles, quality gates
│   ├── 02-prd-decomposition-guide.md  # PRD → Epics → Features → Stories → Tasks
│   ├── 03-steering-guide.md     # Writing effective steering files
│   ├── 04-hooks-guide.md        # Automating quality gates (v1 hook schema)
│   ├── 05-work-item-sync-guide.md     # Bidirectional tracker sync
│   └── 06-getting-started.md    # Setup tutorial + first conversation scripts
│
├── templates/                   # Copy-paste starters for your own project
│   ├── steering/                # 13 steering file templates
│   ├── specs/                   # 5 spec file templates
│   ├── hooks/                   # 10 hook templates + shared scripts
│   └── workflows/               # 6 GitHub Actions templates + adoption guide
│
└── examples/
    ├── example-1-saas-platform/ # Container-based SaaS (Python/FastAPI/ECS/Aurora)
    │   ├── sample-prd/          # Rich PRD: vision, personas, epics, NFRs
    │   ├── .kiro/               # Steering, hooks, specs, MCP config
    │   ├── infra/               # Terraform: bootstrap, root, Cognito module
    │   ├── src/                 # FastAPI auth package (story A2 output)
    │   ├── tests/               # Unit tests for the auth package
    │   └── docs/decisions/      # ADRs produced as story deliverables
    │
    └── example-2-data-pipeline/ # Serverless pipeline (Python/Lambda/Kinesis/S3)
        ├── sample-prd/          # Rich PRD: event-driven platform requirements
        ├── .kiro/               # Steering, hooks, specs, MCP config
        ├── infra/               # Terraform: ingestion module
        ├── src/                 # Lambda handler + shared layer (story E1 output)
        └── tests/               # Unit tests for handler and layer
```

---

## Three Ways to Use This Repository

### 1. Learn the Methodology

Read the docs in order:

| Guide | What You'll Learn |
|-------|------------------|
| [01 — Process Guide](docs/01-process-guide.md) | The five phases, story lifecycle, quality gates, anti-patterns |
| [02 — PRD Decomposition](docs/02-prd-decomposition-guide.md) | How to take a real PRD through epics → features → stories → tasks |
| [03 — Steering Guide](docs/03-steering-guide.md) | How to write context files that keep Kiro accurate across sessions |
| [04 — Hooks Guide](docs/04-hooks-guide.md) | How to automate quality checks using Kiro's hook system |
| [05 — Work-Item Sync](docs/05-work-item-sync-guide.md) | Bidirectional sync with Azure DevOps or GitHub Issues |
| [06 — Getting Started](docs/06-getting-started.md) | Prerequisites, quick setup, first conversation scripts |

### 2. Study the Examples

Follow the traceability chain in a complete worked example:

**Example 1 (SaaS Platform)** — start here if your project is container-based or uses a relational database.

```
sample-prd/product-requirements.md     → read the PRD
.kiro/steering/product-overview.md     → see how it became persistent context
.kiro/specs/epic-1-user-management/    → see the epic-level decomposition
.kiro/specs/101-authentication/        → see a fully decomposed feature
  └── requirements.md                  → PRD traceability table
  └── design.md                        → DEC-001 through DEC-003
  └── stories/A2-pending-jwt-middleware.md  → gold-standard completed story
src/auth/                              → the actual code A2 produced
tests/unit/auth/                       → the tests A2 produced
docs/decisions/0001-jwt-library-choice.md  → the ADR A2 produced
```

**Example 2 (Data Pipeline)** — start here if your project is serverless or event-driven.

```
sample-prd/product-requirements.md    → event-driven platform requirements
.kiro/steering/                        → serverless-focused steering files
.kiro/specs/101-rest-api-ingestion/    → Lambda + API Gateway feature decomposition
  └── stories/E1-pending-api-gateway-lambda.md  → completed Lambda story
src/                                   → Lambda handler + shared layer
tests/                                 → unit tests
```

Both examples demonstrate the same workflow with different architectures, showing the
methodology is stack-agnostic.

### 3. Copy Templates for Your Own Project

```bash
# Start from an example's .kiro setup
cp -r examples/example-1-saas-platform/.kiro your-project/.kiro

# Or build up from templates
cp templates/steering/product-overview.template.md   your-project/.kiro/steering/product-overview.md
cp templates/specs/requirements.template.md          your-project/.kiro/specs/feature-101/requirements.md
cp templates/hooks/secret-guard.template.json        your-project/.kiro/hooks/secret-guard.json
cp templates/workflows/spec-integrity.template.yml   your-project/.github/workflows/spec-integrity.yml
```

Fill in the bracketed placeholders (`grep -rn '\[YOUR' .kiro/steering/`) and you have a
working spec-driven setup in under 10 minutes.

---

## Prerequisites

| Requirement | Purpose |
|-------------|---------|
| [Kiro IDE](https://kiro.dev) | The AI development environment |
| Git | Version control |
| Node.js (with `npx` on PATH) | Runs MCP servers |
| AWS CLI v2 | AWS deployments (for the infra examples) |
| Terraform >= 1.14 | Infrastructure as Code (for the infra examples) |

**Optional — for work-item sync:**

| Requirement | Purpose |
|-------------|---------|
| `uv` (Python) | AWS documentation MCP server |
| Azure DevOps PAT | Sync with ADO (Example 1) |
| GitHub Token | Sync with GitHub Issues (Example 2) |

The tracker MCP servers in both examples ship `"disabled": true`. Set your token as an
environment variable and flip the flag in `.kiro/settings/mcp.json` to activate sync.

---

## End-to-End Traceability

Traceability is a first-class concern throughout the repo. Here is the complete chain
for a delivered story, using Example 1 / Story A2 as the reference:

```
PRD §Security, §Epic 1
  └─► requirements.md  R2 — "JWT validation middleware for FastAPI" (3 PD, Sprint S1)
        └─► design.md  DEC-003 — "Middleware-based auth via FastAPI Depends"
              └─► story A2  Implementation Tasks 1.1 – 6.4 (all checked off)
                    └─► src/auth/  token.py, jwks.py, dependencies.py, models.py …
                    └─► tests/unit/auth/  test_token.py, test_jwks.py, test_dependencies.py
                    └─► docs/decisions/0001-jwt-library-choice.md  (ADR as story output)
                    └─► work-item-map.yaml  DEV-001 — design deviation documented
```

The `check-spec-integrity.py` hook script validates this chain automatically on every
spec file save, catching broken story references, unchecked tasks on Done stories,
dependency cycles, and capacity mismatches before they accumulate.

---

## What Kiro Does at Each Stage

| Stage | What You Do | What Kiro Does |
|-------|------------|----------------|
| PRD Intake | Share the PRD, discuss epics | Creates `product-overview.md`, `technology-guidelines.md`, epic READMEs |
| Feature Decomposition | Discuss scope and dependencies | Creates `requirements.md`, `design.md`, `tasks.md`, `work-item-map.yaml`, story files |
| Story Planning | Discuss the implementation approach | Adds `## Implementation Tasks` to the story file |
| Implementation | Review and approve | Writes code, checks off tasks, runs validation |
| Delivery | Commit and open PR | CI validates; you merge and sync tracker state |

You make decisions. Kiro manages the artifacts.

---

## Template Inventory

### Steering Templates (13)

| Template | Inclusion Mode | Priority |
|----------|---------------|----------|
| `product-overview.template.md` | always | Required |
| `technology-guidelines.template.md` | always | Required |
| `coding-standards.template.md` | always | Required |
| `repository-structure.template.md` | always | Required |
| `infra-guidelines.template.md` | fileMatch (`infra/**`) | Required if using IaC |
| `work-item-sync-playbook.template.md` | manual | Required for tracker sync |
| `security-guidelines.template.md` | always | Recommended |
| `api-guidelines.template.md` | fileMatch | Recommended |
| `testing-strategy.template.md` | fileMatch | Recommended |
| `observability-guidelines.template.md` | fileMatch | Recommended |
| `domain-glossary.template.md` | always | Optional |
| `pr-conventions.template.md` | manual | Optional |
| `onboarding-guide.template.md` | manual | Optional |

### Spec Templates (5)

| Template | Purpose |
|----------|---------|
| `story-template.md` | Canonical story file with YAML front-matter and AC sections |
| `requirements.template.md` | Feature requirements with PRD traceability table |
| `design.template.md` | Architectural decisions in DEC-NNN format with rollback paths |
| `tasks.template.md` | Sprint-organized checklist with effort and owner columns |
| `work-item-map.template.yaml` | Feature index, capacity per person per sprint, deviation log |

### Hook Templates (10)

| Template | Trigger | Purpose |
|----------|---------|---------|
| `session-context.template.json` | SessionStart | Primes session with current branch and in-flight stories |
| `design-review.template.json` | PostFileCreate | Reviews new files for alignment with coding standards |
| `lint-on-save.template.json` | PostFileSave | Runs linter on save |
| `terraform-validate.template.json` | PostFileSave | Runs `terraform fmt` + `terraform validate` on `.tf` saves |
| `spec-consistency.template.json` | PostFileSave | Validates spec integrity on spec file saves |
| `secret-guard.template.json` | PreToolUse (blocking) | Blocks writes that contain credential patterns |
| `security-scan.template.json` | PostFileSave | Runs security scanner on source files |
| `api-contract-check.template.json` | PostFileSave | Validates API changes against schema |
| `dependency-audit.template.json` | PostFileSave | Audits dependency changes for known vulnerabilities |
| `test-after-task.template.json` | PostTaskExec | Runs tests after each completed spec task |

### CI/CD Workflow Templates (6)

| Template | When It Runs | What It Does |
|----------|-------------|-------------|
| `spec-integrity.template.yml` | On `.kiro/**` changes | Validates spec structure and traceability links |
| `work-item-link-check.template.yml` | On every PR | Verifies `Work-Item:` commit trailer |
| `code-quality.template.yml` | On `src/**` changes | Lint, type-check, test, security scan |
| `terraform-plan.template.yml` | On `infra/**` changes | Posts plan output as PR comment |
| `terraform-apply.template.yml` | On merge to main | Applies Terraform changes |
| `pr-completeness-review.template.yml` | On `story/*` PRs | Checks all tasks checked off and ACs addressed |

See [templates/workflows/README.md](templates/workflows/README.md) for adoption order
and OIDC setup instructions.

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for how to contribute to this repository.

## License

This project is licensed under the MIT-0 License. See [LICENSE](LICENSE) for details.

## Code of Conduct

See [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).
