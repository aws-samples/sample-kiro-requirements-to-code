---
inclusion: fileMatch
fileMatchPattern: "infra/**"
---

# Infrastructure Standards

## Terraform

- **Terraform** is the sole IaC tool. No hand-provisioned resources.
- **Module layout:** `main.tf`, `variables.tf`, `outputs.tf`, `versions.tf` per module.
- **Remote state:** S3 with `use_lockfile = true`, KMS encrypted.
- **Provider pins:** Lock versions in `versions.tf`. Set `required_version`.
- **Quality gates:** `terraform fmt`, `tflint`, `checkov` in CI. Blocking.
- **PR flow:** `plan` on PR (posted as comment), `apply` on merge for dev.
- **Secrets:** Never in `.tf` or `.tfvars`. Use Secrets Manager or SSM.

## [Compute Layer — customize for your stack]

- **Base images:** [Your base image policy]
- **Non-root:** Always. Explicit USER directive.
- **Health checks:** [Your health check standard]
- **Signals:** Handle SIGTERM cleanly.

## AWS Baseline

- **Multi-AZ:** [Which services]
- **KMS:** Customer-managed CMK for [which data]
- **VPC Endpoints:** [Which services use endpoints]
- **Least privilege:** IAM policies with explicit ARNs, never `*`.
- **Encryption in transit:** TLS 1.2+ everywhere.
- **Logging:** [Your logging standard]

## Observability

- **Structured JSON logs:** Include [required fields]
- **Tracing:** [X-Ray / OTEL / ADOT]
- **Metrics:** [Namespace, dimensions]
- **Alarms:** [What triggers alerts]
