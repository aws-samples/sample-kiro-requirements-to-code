# Requirements — Terraform Foundation (Feature 301)

**Parent Epic:** Epic 3 — Platform Infrastructure
**PI:** PI-1 · **Effort:** 12 PD · **Owners:** Alice, Bob

## Feature Intent

Establish the Terraform infrastructure foundation that all other features deploy onto. Includes remote state, VPC networking, ECS cluster, Aurora database, and local quality gates. This is the bedrock that must be in place before any application code can be deployed.

## In Scope (PI 1)

- Terraform remote state (S3 + native locking)
- Module layout and conventions
- VPC with public/private subnets, NAT, flow logs
- ECS Fargate cluster
- Aurora PostgreSQL Serverless v2 cluster
- S3 bucket for file attachments
- KMS keys for encryption
- Pre-commit quality gates (fmt, validate, tflint, checkov)

## Out of Scope (PI 1)

- CI/CD pipeline — plan on PR, apply on merge (Feature 302, PI 1; adopts `templates/workflows/`)
- CloudFront CDN (frontend in PI 2)
- WAF rules (PI 2)
- Multi-region DR (PI 3)
- Cost optimization tooling (PI 2)

## Requirements Traceability

| Req | Description | PRD Section | Stories (PD) |
|-----|-------------|-------------|--------------|
| R1 | Remote state + module layout + pre-commit | §Technology | I1 (3) |
| R2 | VPC + subnets + NAT + flow logs | §Availability | I2 (3) |
| R3 | ECS Fargate cluster + task definitions | §Technology | I3 (3) |
| R4 | Aurora Serverless v2 + KMS + S3 | §Security, §Scalability | I4 (3) |

**Total effort:** 12 PD · **Stories:** 4
