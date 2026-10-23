# Example 2: StreamProcess — Real-Time Data Pipeline

## About This Example

StreamProcess is a serverless event-driven data processing platform built on AWS. This example demonstrates spec-driven development for a Lambda/Step Functions architecture — a different pattern from the container-based Example 1.

## What's Demonstrated

| Aspect | How It's Shown |
|--------|---------------|
| **PRD Intake** | `sample-prd/product-requirements.md` → serverless-focused steering |
| **Epic Decomposition** | PRD → 4 Epics (Ingestion, Processing, Delivery, Platform) |
| **Feature Planning** | 1 feature fully decomposed (REST API Ingestion) |
| **Story Creation** | 4 stories with front-matter, scope, acceptance criteria |
| **Implementation Tasks** | 2 stories (E1 Lambda patterns, E4 Terraform module) with complete task breakdowns showing done state |
| **Steering Files** | 4 files with serverless-specific standards |
| **Hooks** | 5 hooks (Lambda validation, Terraform validate, Python lint, secret guard, spec consistency) |
| **MCP Integration** | GitHub Issues + AWS Docs (lighter than ADO setup; the GitHub server ships `"disabled": true` — set `GITHUB_TOKEN`, then flip the flag) |
| **Deviation Tracking** | DEV-001 (S3 schema storage vs the PRD's Schema Registry mandate) in `101-rest-api-ingestion/work-item-map.yaml` |
| **Pipeline Config** | YAML-based pipeline definition pattern in coding standards |

## Technology Stack

| Component | Technology |
|-----------|-----------|
| Language | Python 3.12 |
| Compute | AWS Lambda |
| Orchestration | Step Functions (Express) |
| Streaming | Kinesis Data Streams |
| API | API Gateway REST |
| Storage | S3 (Parquet), DynamoDB |
| IaC | Terraform |
| CI/CD | GitHub Actions |

## Spec Structure

```
.kiro/specs/
├── _story-template.md
├── epic-1-ingestion/
│   └── README.md                          # Epic overview
└── 101-rest-api-ingestion/                # Feature: REST Ingestion
    ├── requirements.md                    # Traceability to PRD
    ├── design.md                          # DEC-001 through DEC-003
    ├── tasks.md                           # Sprint checklist
    ├── work-item-map.yaml                 # Index + capacity + DEV-001
    └── stories/
        ├── README.md                           # Conventions + GitHub Issues mapping
        ├── E1-pending-api-gateway-lambda.md    # ✅ Done — Lambda patterns
        ├── E2-pending-schema-validation-dlq.md # New — AC only
        ├── E3-pending-kinesis-persistence.md   # New — AC only
        └── E4-pending-terraform-ingestion.md   # ✅ Done — Terraform patterns
```

## Key Patterns to Study (Different from Example 1)

1. **Serverless steering** — `infra-guidelines.md` covers Lambda DLQ, Step Functions, Kinesis patterns
2. **Lambda coding standards** — Powertools integration, handler pattern, layer structure
3. **Data standards** — JSON Schema, UUIDv7, Parquet partitioning in `coding-standards.md`
4. **Design decisions** — DEC-001 shows API Gateway vs ALB trade-off for serverless
5. **Story E1** — Shows Lambda-specific implementation tasks (layers, Powertools, API Gateway events); its output ships in `src/`
6. **Story E4** — Shows a completed Terraform story whose acceptance criteria verify against the actual module in `infra/terraform/`
7. **GitHub Issues integration** — Lighter MCP setup vs Azure DevOps in Example 1 (see `stories/README.md` for the field mapping)

## How This Differs from Example 1

| Dimension | Example 1 (SaaS Platform) | Example 2 (Data Pipeline) |
|-----------|--------------------------|--------------------------|
| Compute | ECS Fargate (containers) | Lambda (serverless) |
| Architecture | Request-response API | Event-driven pipeline |
| Database | Aurora PostgreSQL | S3 + DynamoDB |
| Multi-tenancy | Schema-per-tenant | Pipeline-per-source |
| Tracker | Azure DevOps | GitHub Issues |
| Language | Python + FastAPI | Python + Powertools |
| Hook focus | RBAC + tenant isolation | Lambda conventions + schema |

## How to Use This Example

1. Read the PRD (`sample-prd/product-requirements.md`)
2. Notice how serverless constraints shape the steering files differently
3. Study the design decisions — serverless trade-offs are different from container ones
4. Look at story E1 for Lambda-specific implementation patterns
5. Compare with Example 1 to see how the same spec-driven workflow adapts to different architectures
