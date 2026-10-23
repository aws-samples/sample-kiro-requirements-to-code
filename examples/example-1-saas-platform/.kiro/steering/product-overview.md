---
inclusion: always
---

# TaskFlow — Product Overview

## Vision

TaskFlow is a multi-tenant project management SaaS on AWS. It enables teams to manage projects, track tasks, and collaborate. Target market: SMBs with 10-500 users per tenant.

## Architecture Layers

1. **Cloud Infrastructure** — AWS (VPC, ECS Fargate, Aurora, S3, Cognito). Managed via Terraform.
2. **Platform Services** — Authentication (Cognito), Secrets (Secrets Manager), Observability (CloudWatch + X-Ray).
3. **Domain Services** — FastAPI applications deployed on ECS Fargate. One service per bounded context.
4. **Application Layer** — React frontend (future PI), REST API for integrations.

## Epics

| Epic | Description | PI |
|------|-------------|-----|
| 1. User & Tenant Management | Auth, RBAC, tenant provisioning, profiles | PI 1 |
| 2. Project & Task Management | Projects, tasks, boards, activity | PI 1-2 |
| 3. Platform Infrastructure | IaC, CI/CD, observability, cost mgmt | PI 1 |
| 4. Integrations & API | REST API, webhooks, third-party | PI 2 |

## Multi-Tenancy Model

- **Database isolation:** Schema-per-tenant in Aurora PostgreSQL
- **Request context:** Tenant ID extracted from JWT claims
- **Resource isolation:** S3 prefix per tenant, IAM boundary per tenant
- **Compute:** Shared ECS cluster behind an ALB; tenant context comes from the JWT tenant claim, not a per-tenant routing tier

## Key Terminology

| Term | Definition |
|------|-----------|
| Tenant | A customer organization using TaskFlow |
| Workspace | A project container within a tenant |
| Member | A user within a tenant with assigned role |
| Task | An actionable work item within a project |

## Non-Functional Requirements (Key)

- **Security:** KMS encryption, tenant isolation, OWASP Top 10, audit trail
- **Scalability:** 100 tenants year 1, p95 < 200ms reads
- **Availability:** 99.9% SLA, multi-AZ, zero-downtime deploys
- **Compliance:** SOC 2 Type II readiness
