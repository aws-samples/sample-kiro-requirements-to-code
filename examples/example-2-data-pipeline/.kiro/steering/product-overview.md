---
inclusion: always
---

# StreamProcess — Product Overview

## Vision

StreamProcess is a serverless, event-driven data processing platform on AWS. Data engineers define pipelines as configuration; the platform handles ingestion, transformation, routing, and delivery. No infrastructure management for pipeline authors.

## Architecture Layers

1. **Ingestion** — API Gateway + Lambda (sync), Kinesis Data Streams (async). Schema validation at entry.
2. **Processing** — Step Functions orchestration, Lambda compute. Sequential, parallel, conditional.
3. **Delivery** — S3 (data lake), DynamoDB (lookup), EventBridge (fan-out).
4. **Platform** — Terraform IaC, CI/CD, observability, cost attribution.

## Epics

| Epic | Description | PI |
|------|-------------|-----|
| 1. Ingestion | REST API + Kinesis + schema validation + DLQ | PI 1-2 |
| 2. Processing | Step Functions pipelines + Lambda transforms | PI 1-2 |
| 3. Delivery | S3, DynamoDB, EventBridge destinations | PI 1-2 |
| 4. Platform | Terraform, CI/CD, dashboards, cost | PI 1-2 |

## Data Flow

```
Sources → [API Gateway / Kinesis] → Schema Validation → [Step Functions Pipeline]
→ Lambda Transform(s) → [S3 / DynamoDB / EventBridge] → Consumers
```

## Key Terminology

| Term | Definition |
|------|-----------|
| Pipeline | A configured sequence of processing steps from source to destination |
| Source | An event producer registered in the platform |
| Destination | A configured output target (S3 bucket, DDB table, EventBridge bus) |
| Transform | A Lambda function that processes/enriches an event |
| Schema | The expected structure of events from a source (JSON Schema) |
| DLQ | Dead-letter queue for events that fail validation or processing |

## Non-Functional Requirements (Key)

- **Latency:** < 100ms ingestion, < 5s processing, < 30s end-to-end
- **Throughput:** 10K events/second per pipeline
- **Reliability:** At-least-once delivery, DLQ at every stage
- **Security:** API key auth, KMS encryption, IAM least-privilege
