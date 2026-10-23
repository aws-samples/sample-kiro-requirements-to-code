# Example 1: TaskFlow — Multi-Tenant SaaS Platform

## About This Example

TaskFlow is a multi-tenant project management SaaS built on AWS. This example demonstrates the full spec-driven development workflow from PRD through implementation for a Python/FastAPI backend deployed on ECS Fargate.

## What's Demonstrated

| Aspect | How It's Shown |
|--------|---------------|
| **PRD Intake** | `sample-prd/product-requirements.md` → extracted into steering files |
| **Epic Decomposition** | 4 epics identified in the PRD → README files for the 2 epics with active features |
| **Feature Planning** | 2 features fully decomposed (Authentication, Infrastructure) |
| **Story Creation** | 8 stories with front-matter, scope, acceptance criteria |
| **Implementation Tasks** | 3 stories (A1, A2, I1) with complete task breakdowns showing done state |
| **Steering Files** | 5 files covering product, tech, coding, infra, sync |
| **Hooks** | 6 hooks (Terraform validate, design review, Python lint, secret guard, spec consistency, session context) |
| **MCP Integration** | Azure DevOps + GitHub + AWS Docs servers (tracker servers ship `"disabled": true` — set `AZURE_DEVOPS_PAT` / `GITHUB_TOKEN`, then flip the flag) |
| **Work-Item Sync** | Complete sync playbook with aliases and field mappings |
| **Deviation Tracking** | DEV-001 recorded in `101-authentication/work-item-map.yaml`, captured in `docs/decisions/0001-jwt-library-choice.md` |

## Technology Stack

| Component | Technology |
|-----------|-----------|
| Language | Python 3.12 |
| Framework | FastAPI |
| Database | Aurora PostgreSQL Serverless v2 |
| Compute | ECS Fargate |
| Auth | AWS Cognito |
| IaC | Terraform |
| CI/CD | GitHub Actions |

## Spec Structure

```
.kiro/specs/
├── _story-template.md
├── epic-1-user-management/
│   └── README.md                          # Epic overview
├── epic-3-platform-infrastructure/
│   └── README.md                          # Epic overview (Feature 301's parent)
├── 101-authentication/                    # Feature: Auth & AuthZ
│   ├── requirements.md                    # Traceability to PRD
│   ├── design.md                          # DEC-001 through DEC-003
│   ├── tasks.md                           # Sprint checklist
│   ├── work-item-map.yaml                 # Index + capacity + DEV-001
│   └── stories/
│       ├── README.md                      # Conventions + dependency graph
│       ├── A1-ADO-12301-cognito-terraform.md  # ✅ Done — full impl tasks
│       ├── A2-ADO-12302-jwt-middleware.md      # ✅ Done — full impl tasks
│       ├── A3-ADO-12303-rbac.md               # Planned — impl tasks added (sprint 2)
│       └── A4-ADO-12304-tenant-isolation.md   # New — AC only
└── 301-terraform-foundation/              # Feature: Infra
    ├── requirements.md
    ├── design.md                          # DEC-101 through DEC-103
    ├── tasks.md
    ├── work-item-map.yaml
    └── stories/
        ├── I1-ADO-12311-terraform-foundation.md  # ✅ Done — full impl tasks
        ├── I2-ADO-12312-vpc-networking.md         # New — AC only
        ├── I3-ADO-12313-ecs-cluster.md            # New — AC only
        └── I4-ADO-12314-aurora-s3-kms.md          # New — AC only
```

Architecture Decision Records produced by stories live outside `.kiro/` at
`docs/decisions/` — see ADR 0001 for the story-A2 library decision that
`work-item-map.yaml` tracks as DEV-001.

## Key Patterns to Study

1. **Story A1** — Shows a completed infrastructure story with implementation tasks checked off; `trackerId: ADO-12301` shows a post-sync state
2. **Story A2** — Shows a completed application code story with test tasks; its actual output ships in `src/auth/` and `tests/`
3. **Story A3** — Shows the Spec PR workflow: a story that has had a Sprint 2 planning session with impl tasks added, but implementation not yet started
4. **Story A4** — Shows how multi-tenancy concerns are captured in acceptance criteria
5. **design.md** — Shows the DEC-NNN format for architectural decisions with rollback paths
6. **work-item-map.yaml (101)** — Shows capacity planning, deferred items, and a real recorded deviation (DEV-001 → `docs/decisions/0001-jwt-library-choice.md`)
7. **work-item-map.yaml (301)** — Shows DEV-002 recording a post-implementation discovery; links to `docs/decisions/0002-terraform-state-management.md`
8. **Story I1** — Shows how scope that belongs to a sibling feature (CI/CD, Feature 302) is kept out of a story rather than half-claimed
9. **Tracker sync** — All Done stories use real ADO IDs (ADO-12301 through ADO-12311); see `work-item-map.yaml` for the complete state after a PI-1 sprint sync

## How to Use This Example

1. Read the PRD (`sample-prd/product-requirements.md`)
2. See how it was decomposed into steering files (`.kiro/steering/`)
3. Follow the trail: Epic README → Feature requirements → Design → Stories
4. Study a completed story (A1 or A2) to see the full lifecycle
5. Study story A3 to see the planning artifact (impl tasks added, no code yet)
6. Compare ADRs: 0001 (library choice from A2) and 0002 (infra decision from I1)
7. Copy and adapt for your own project
