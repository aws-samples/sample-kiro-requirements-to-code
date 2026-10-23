---
inclusion: fileMatch
fileMatchPattern: "infra/**"
---

# Infrastructure Standards — StreamProcess

## Terraform

- Terraform is the sole IaC tool. No CloudFormation, no SAM.
- Module layout: `main.tf`, `variables.tf`, `outputs.tf`, `versions.tf`, `README.md`.
- Remote state: S3 with `use_lockfile = true`, KMS encrypted.
- Provider pin: `aws ~> 5.0`, `terraform >= 1.14`.
- Quality gates: `terraform fmt`, `tflint`, `checkov` in CI. Blocking.

## Serverless Conventions

- Every Lambda function has:
  - Dead-letter queue (SQS)
  - CloudWatch log group with retention (14 days dev, 90 days prod)
  - X-Ray tracing enabled
  - IAM role with least-privilege policy
  - Environment variables for configuration (never hardcoded)
- Step Functions:
  - Express workflows for < 5 min pipelines
  - Error catchers on every state with DLQ routing
  - X-Ray tracing enabled
  - CloudWatch Logs for execution history

## Event Infrastructure

- Kinesis: on-demand capacity mode (no shard management for PI 1)
- EventBridge: custom bus per pipeline category, not the default bus
- SQS DLQs: 14-day retention, alarm on message count > 0
- API Gateway: usage plans + API keys, throttling per source

## S3 Data Lake

- Bucket per environment: `streamprocess-{env}-data-{account-id}`
- Lifecycle rules: transition to IA after 30 days, Glacier after 90
- Versioning enabled for delivery buckets
- Partitioning: `pipeline-name/year=YYYY/month=MM/day=DD/`
- Format: Parquet with Snappy compression

## Observability

- CloudWatch namespace: `StreamProcess/{Environment}`
- Metrics per pipeline: EventsIngested, EventsProcessed, EventsFailed, ProcessingLatency
- Dashboard per pipeline: auto-created via Terraform
- Alarms: DLQ depth > 0, error rate > 5%, latency p95 > 10s

## Security

- KMS CMK per data category (events, configs, logs)
- Lambda in VPC only when accessing VPC resources
- API Gateway: WAF in production (PI 2)
- Secrets: SSM Parameter Store (SecureString) for API keys, connection strings
