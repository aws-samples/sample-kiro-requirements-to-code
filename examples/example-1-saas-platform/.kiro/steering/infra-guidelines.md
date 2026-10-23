---
inclusion: fileMatch
fileMatchPattern: "infra/**"
---

# Infrastructure Standards

## Terraform

- **Terraform** is the sole IaC tool. No hand-provisioned resources.
- **Module layout:** `main.tf`, `variables.tf`, `outputs.tf`, `versions.tf` in every module.
- **Remote state:** S3 bucket with `use_lockfile = true` (Terraform 1.14+), KMS encrypted.
- **Provider pins:** Lock `aws`, `random`, `null` providers. Set `required_version`.
- **Quality gates:** `terraform fmt`, `tflint`, `checkov` in pre-commit and CI. Blocking.
- **PR flow:** `plan` posted as PR comment, `apply` on merge for dev, manual approval for prod.
- **Secrets:** Never in `.tf` or `.tfvars`. Use data sources against Secrets Manager or SSM.
- **Multi-tenancy:** Never hardcode tenant identifiers. Use `for_each` over tenant config.

### Module Conventions

```
infra/terraform/modules/<module-name>/
├── main.tf          # Resources + header comment describing purpose
├── variables.tf     # Typed, described inputs (required = no default)
├── outputs.tf       # Named outputs with descriptions
├── versions.tf      # Provider + Terraform version constraints
└── README.md        # Usage example, inputs/outputs table
```

### Naming
- Resources: `${var.name_prefix}-<resource-type>` (e.g., `taskflow-dev-vpc`)
- Use `name_prefix` variable consistently across all modules.
- Tags: every resource gets `var.tags` merged with a `Name` tag.

### Variables
- Required variables: no default value.
- Optional variables: sensible defaults + clear description.
- All variables have `type` and `description`.
- Use `validation` blocks for inputs with known constraints.

## Containers

- **Base images:** `python:3.12-slim` for application containers.
- **Non-root:** Always. Explicit `USER` directive in final stage.
- **Multi-stage builds:** Build dependencies never in final image.
- **Scanning:** ECR enhanced scanning. No unresolved High/Critical CVEs at merge.
- **Tags:** Immutable. Git SHA or SemVer. Never `latest` in production.
- **Health:** `/health` liveness, `/health/ready` readiness. Both respond < 1s.
- **Signals:** Handle SIGTERM cleanly. Flush connections, exit 0.

## AWS Baseline

- **Multi-AZ:** Aurora, ALB, ECS tasks spread across AZs.
- **KMS:** Customer-managed CMK for RDS, S3, Secrets Manager.
- **VPC Endpoints:** Target state — interface endpoints for S3, Secrets Manager, ECR, CloudWatch. Deferred to PI 2 (see Feature 301 `work-item-map.yaml`); NAT egress until then.
- **Least privilege:** IAM policies list explicit resource ARNs, never `*`.
- **Encryption in transit:** TLS 1.2+ on all endpoints. ALB terminates TLS.
- **Logging:** VPC Flow Logs, ALB access logs to S3, CloudTrail enabled.

## Observability

- **Structured JSON logs:** Include `tenant_id`, `request_id`, `trace_id`.
- **X-Ray tracing:** Instrumented in FastAPI middleware.
- **CloudWatch metrics:** Custom namespace per service with tenant dimension.
- **Alarms:** 5xx rate, p95 latency, ECS task failures, Aurora connections.
