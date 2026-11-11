# Requirements — REST API Ingestion (Feature 101)

**Parent Epic:** Epic 1 — Ingestion Layer
**PI:** PI-1 · **Effort:** 12 PD · **Owners:** Dana, Eric

## Feature Intent

Implement the synchronous REST API ingestion endpoint that allows event publishers to submit events via HTTPS. Events are validated against registered schemas, acknowledged with a correlation ID, and routed to the processing pipeline.

## In Scope (PI 1)

- API Gateway REST API with API key authentication
  - Note (DEV-002): authentication is IAM/SigV4 (`authorization = "AWS_IAM"`); the API key is kept for metering and throttling only. See `docs/THREAT-MODEL.md` E2-T01/E2-T02.
- Lambda ingestion handler (validate, acknowledge, route)
- JSON Schema validation against registered schemas
- Dead-letter queue for invalid events (with metadata: source, schema, error)
- Event persistence to Kinesis before acknowledgment (durability guarantee)
- Correlation ID generation and propagation
- CloudWatch metrics (events received, validated, rejected)
- Terraform module for the complete ingestion stack

## Out of Scope (PI 1)

- Kinesis consumer ingestion (Feature 103, PI 2)
- Rate limiting per source (PI 2, needs usage analytics)
- Batch event submission (PI 2)
- Custom validation rules beyond JSON Schema (PI 2)

## Requirements Traceability

| Req | Description | PRD Section | Stories (PD) |
|-----|-------------|-------------|--------------|
| R1 | API Gateway + Lambda + API key auth | §Tech, §Security | E1 (3) |
| R2 | Schema validation + DLQ routing | §Reliability | E2 (4) |
| R3 | Event persistence + correlation ID | §Reliability, §Performance | E3 (3) |
| R4 | Terraform module for ingestion stack | §Tech | E4 (2) |

**Total effort:** 12 PD · **Stories:** 4
