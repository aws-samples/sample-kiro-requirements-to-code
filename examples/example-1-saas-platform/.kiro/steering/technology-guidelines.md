---
inclusion: always
---

# Technology Guidelines

## Mandated Stack

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| Cloud | AWS | Company standard |
| Backend | Python 3.12 + FastAPI | Team expertise, async, OpenAPI gen |
| Database | Aurora PostgreSQL Serverless v2 | Multi-tenant, auto-scaling, managed |
| IaC | Terraform >= 1.14 | Declarative, state management |
| CI/CD | GitHub Actions | Integrated with repo |
| Containers | ECS Fargate | Serverless, no node ops |
| Auth | AWS Cognito | Managed OIDC, user pools |
| Storage | S3 | File attachments, assets |
| Secrets | AWS Secrets Manager | Rotation, IAM-scoped access |
| OS | Linux (all components) | Mandatory |

## Constraints

- All new code must target Linux. No Windows dependencies.
- Python 3.12+ with type hints mandatory.
- FastAPI with Pydantic v2 for all API services.
- No ORM — use raw SQL with asyncpg for performance and control.
- Alembic for database migrations.
- Pytest for all testing.
- Docker multi-stage builds for all container images.
- Terraform modules must be reusable across environments.

## Compatibility Matrix

| Component | Target | Flexibility |
|-----------|--------|-------------|
| Python | 3.12 | Low — team standard |
| FastAPI | 0.110+ | Medium — track latest |
| PostgreSQL | 16 (Aurora) | Low — managed service |
| Terraform | >= 1.14 | Medium — pin per module |
| ECS | Fargate | Low — serverless mandate |
| Container base | python:3.12-slim | Medium — distroless future |

## Security Baseline

- All secrets via Secrets Manager or SSM Parameter Store (SecureString)
- Never in environment variables, .env files, or Terraform state
- KMS CMK for encryption at rest (RDS, S3, ECS secrets)
- TLS 1.2+ for all in-transit communication
- IAM roles with least-privilege per service
- Security scanning: Bandit (Python), Checkov (Terraform), Trivy (containers)
