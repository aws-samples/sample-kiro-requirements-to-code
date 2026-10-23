# Epic 1: Ingestion Layer

## Vision

Provide reliable, schema-validated event ingestion that accepts events from multiple sources types, validates them against registered schemas, and routes invalid events to dead-letter queues for investigation.

## Capabilities

- REST API ingestion (synchronous, < 100ms)
- Kinesis stream ingestion (high-throughput, ordered)
- Schema registry with JSON Schema validation
- Dead-letter queue with diagnostic metadata
- Source registration and management

## Features

| Feature | ID | PI | Status | Stories | Effort |
|---------|----|----|--------|---------|--------|
| REST API Ingestion | 101 | PI 1 | In Progress | 4 | 12 PD |
| Schema Registry | 102 | PI 1 | Planned | 3 | 8 PD |
| Kinesis Ingestion | 103 | PI 2 | Future | TBD | TBD |

## Dependencies

- Depends on: Epic 4 (Infrastructure — API Gateway, Lambda, KMS must exist)
- Blocks: Epic 2 (Processing — needs validated events from ingestion)

## Success Metrics

- Events ingested at < 100ms p95 latency
- Zero valid events lost (at-least-once guarantee)
- Invalid events captured in DLQ with full diagnostic context
- 99.9% API availability
