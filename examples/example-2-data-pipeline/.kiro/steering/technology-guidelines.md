---
inclusion: always
---

# Technology Guidelines

## Mandated Stack

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| Cloud | AWS | Company standard |
| Compute | Lambda (Python 3.12) | Serverless, event-driven, pay-per-use |
| Orchestration | Step Functions (Express) | Low-latency workflows |
| Streaming | Kinesis Data Streams | High-throughput, ordered events |
| Event routing | EventBridge | Serverless event bus, fan-out |
| API | API Gateway REST | Managed, throttling, API keys |
| Data lake | S3 + Parquet | Columnar, efficient queries |
| Lookup store | DynamoDB | Single-digit ms reads |
| Schema | S3 (JSON Schema files) in PI 1; EventBridge Schema Registry planned PI 2 | Simple now, managed/versioned later — deviation DEV-001 in Feature 101's work-item map |
| IaC | Terraform >= 1.14 | Declarative, modular |
| CI/CD | GitHub Actions | Repository integration |
| OS | Linux (Lambda runtime) | Mandatory |

## Constraints

- All compute is serverless. No EC2, no containers.
- Python 3.12 with type hints for all Lambda functions.
- Lambda functions must be < 50MB deployment package (use layers for shared deps).
- Step Functions: Express workflows for < 5 min processing, Standard for longer.
- No VPC for Lambda unless accessing VPC resources (cold start penalty).
- Terraform modules must be reusable across environments.
- All data at rest encrypted with KMS CMK.

## Lambda Standards

- Handler pattern: `def handler(event, context) -> dict`
- Use Powertools for AWS Lambda (logging, tracing, metrics, validation)
- Maximum execution time: 60 seconds per transform step
- Memory: Right-sized per function (start 256MB, adjust based on metrics)
- Layers: shared utilities in a Lambda Layer (max 5 layers per function)

## Data Standards

- Events are JSON. Schema defined in JSON Schema Draft 2020-12.
- Timestamps: ISO 8601 UTC (e.g., `2025-01-15T10:30:00Z`)
- IDs: UUIDv7 (time-ordered, sortable)
- S3 output: Parquet with Snappy compression, partitioned by date + source
- Naming: `s3://bucket/pipeline-name/year=YYYY/month=MM/day=DD/`

## Security Baseline

- API keys for event publishers (rotated quarterly)
- IAM execution roles per Lambda function (least privilege)
- KMS CMK for S3, DynamoDB, Kinesis, SQS encryption
- No hardcoded secrets — SSM Parameter Store or Secrets Manager
- CloudTrail for audit trail on all API calls
