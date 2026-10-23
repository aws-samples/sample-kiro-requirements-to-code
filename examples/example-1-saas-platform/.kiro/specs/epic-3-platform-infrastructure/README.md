# Epic 3: Platform Infrastructure

## Vision

Provide the foundational AWS infrastructure, delivery pipelines, and operational
tooling that every TaskFlow feature deploys onto — fully managed as code, so a new
environment is a `terraform apply` away and no resource exists that Git does not
describe.

## Capabilities

- Multi-tenant AWS infrastructure (VPC, ECS Fargate, Aurora, S3, KMS)
- Infrastructure as Code (Terraform with remote state and native locking)
- CI/CD pipeline (GitHub Actions — plan on PR, apply on merge)
- Observability (CloudWatch, X-Ray)
- Secrets management (Secrets Manager)
- Cost monitoring and optimization

## Features

| Feature | ID | PI | Status | Stories | Effort |
|---------|----|----|--------|---------|--------|
| Terraform Foundation | 301 | PI 1 | In Progress | 4 | 12 PD |
| CI/CD Pipeline | 302 | PI 1 | Planned | TBD | TBD |
| Observability & Cost | 303 | PI 2 | Future | TBD | TBD |

Feature 302 adopts the ready-made workflows in `templates/workflows/`
(terraform-plan, terraform-apply, code-quality, spec-integrity) against the
state backend Feature 301 provides.

## Dependencies

- Depends on: nothing — this epic is the base layer
- Blocks: Epic 1 and Epic 2 deployments — application features need VPC, ECS, and Aurora before anything ships

## Success Metrics

- Infrastructure deploys via Terraform with zero manual steps
- `terraform plan` posted on every infrastructure PR; apply gated on merge (Feature 302)
- No high-severity findings from security scanning in production config
- New environment stood up from scratch in under one day
