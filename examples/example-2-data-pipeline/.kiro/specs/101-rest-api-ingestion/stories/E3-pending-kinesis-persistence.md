---
trackerId: pending
ref: E3
parent: 101
title: "Kinesis persistence and correlation ID propagation"
state: New
sprint: S2
owner: eric
effort: 3
priority: 1
tags: [ingestion, kinesis, PI1]
dependsOn: [E1, E4]
lastSync: 1970-01-01T00:00:00Z
---

## Context

Fourth and final story in Feature 101, covering requirement R3. Implements DEC-002 (Kinesis for event durability) and closes the loop on DEC-003 (validate then persist): the handler built in E1 now writes each validated event to Kinesis before returning 202, so an acknowledgment means the event is durable and replayable.

## Goal

As an event publisher, I want my event persisted to a durable, ordered stream before I get a 202 so that an acknowledgment is a real durability guarantee and the event can be replayed if downstream processing fails.

## Scope

- Kinesis Data Stream in on-demand capacity mode with a KMS CMK and 24-hour retention, added to the `ingestion` Terraform module from E4
- Scoped `kinesis:PutRecord` and `kinesis:PutRecords` grants on the stream ARN added to the execution role, plus the `kms:GenerateDataKey` grant the stream requires
- `EVENT_STREAM_NAME` published to the function as an environment variable, never hardcoded
- Record envelope written to Kinesis: `correlation_id`, `event_id` (UUIDv7), `schema_name`, `schema_version`, `source`, `ingested_at` (ISO 8601 UTC), and the original event body
- Partition key strategy: derived from the publisher-supplied `X-Partition-Key` header when present, falling back to `source` so per-source ordering is preserved, and to `event_id` when neither is available — documented so publishers understand the ordering guarantee they get
- Correlation ID propagation: generated in E1, attached to the Powertools logger, echoed in the 202 response, carried in the record envelope, and returned in the `X-Correlation-Id` response header so consumers can trace an event end to end
- Batched `PutRecords` with per-record partial failure handling: inspect `FailedRecordCount`, retry only the failed records with exponential backoff and jitter, and route records still failing after the retry budget to the E4 dead-letter queue with the Kinesis error code and message attached
- Persistence failures return 503 with RFC 7807 Problem Details rather than a false 202
- CloudWatch metrics via Powertools: `EventsPersisted`, `EventsPersistFailed`, `KinesisPartialFailures`, `PersistLatencyMs` in the `StreamProcess/{Environment}` namespace
- Unit tests with a stubbed Kinesis client covering success, full failure, partial failure with successful retry, and partial failure exhausting retries
- Integration test asserting a published event is readable from the stream with the same correlation ID

## Out of Scope

- Kinesis consumers and the Step Functions processing pipeline (Feature 201)
- Kinesis consumer-based ingestion for the high-throughput path — deferred to the next PI per `work-item-map.yaml`
- Provisioned shard mode and shard-level capacity planning — on-demand only in PI 1 per `infra-guidelines.md`
- Enhanced fan-out consumers
- Extended retention beyond 24 hours
- Batch event submission endpoint (PI 2)
- Cross-region stream replication

## Dependencies

- Requires: E1 (provides the ingestion handler, the correlation ID generation and the RFC 7807 response helpers this story extends)
- Requires: E4 (provides the Terraform module the Kinesis stream, IAM grants and environment variable are added to, and the dead-letter queue used for records that exhaust their retries)
- Blocks: Feature 201 (Processing Pipeline, Epic 2), which consumes this stream

## Acceptance Criteria

- **Given** a validated event, **When** the handler processes it, **Then** the event is written to Kinesis before the 202 is returned, and the response body still carries `correlation_id` and `status: accepted`.
- **Given** a Kinesis write that fails for every record, **When** the handler completes, **Then** the response is 503 with RFC 7807 Problem Details and no 202 is returned, so the publisher knows to retry.
- **Given** a publisher-supplied `X-Partition-Key` header, **When** the record is written, **Then** that value is used as the Kinesis partition key.
- **Given** no `X-Partition-Key` header, **When** the record is written, **Then** the partition key falls back to `source`, so all events from one source land on the same shard and retain their relative order.
- **Given** neither a partition key header nor a resolvable source, **When** the record is written, **Then** `event_id` is used as the partition key and a warning is logged.
- **Given** a record written to the stream, **When** a consumer deserializes it, **Then** the envelope contains `correlation_id`, `event_id`, `schema_name`, `schema_version`, `source`, `ingested_at` as ISO 8601 UTC, and the original event body unchanged.
- **Given** a request, **When** the response is returned, **Then** the `X-Correlation-Id` header carries the same value as the response body and as the `correlation_id` in the Kinesis envelope.
- **Given** any log line emitted while handling a request, **When** I inspect it, **Then** it carries the correlation ID injected into the Powertools logger.
- **Given** a `PutRecords` call returning `FailedRecordCount = 2` out of 10, **When** the handler retries, **Then** only the 2 failed records are resubmitted, the 8 successful records are not duplicated, and backoff between attempts is exponential with jitter.
- **Given** records still failing after the retry budget is exhausted, **When** the handler gives up, **Then** those records are sent to the dead-letter queue from E4 with the Kinesis `ErrorCode`, `ErrorMessage`, correlation ID and original body, and `EventsPersistFailed` is incremented by the number of lost records.
- **Given** the Kinesis stream in Terraform, **When** I inspect it, **Then** `stream_mode` is `ON_DEMAND`, `encryption_type` is `KMS` with a customer-managed key, and retention is 24 hours.
- **Given** the execution role, **When** I inspect its policy, **Then** `kinesis:PutRecord` and `kinesis:PutRecords` are scoped to the stream ARN only, with no wildcard resource.
- **Given** the stream name is needed at runtime, **When** I inspect the function configuration, **Then** it arrives as the `EVENT_STREAM_NAME` environment variable and appears nowhere in the source as a literal.
- **Given** a batch of events is persisted, **When** metrics are flushed, **Then** `EventsPersisted`, `KinesisPartialFailures` and `PersistLatencyMs` are published to the `StreamProcess/{Environment}` namespace.
- **Given** the added latency of the Kinesis write, **When** I measure end-to-end response time in dev, **Then** p95 for a warm invocation stays under 100 ms as required by DEC-001.
- **Given** the test suite, **When** CI runs, **Then** `ruff check`, `ruff format --check`, `mypy` and `pytest` all pass, with coverage for the success, full-failure, partial-failure-then-success and retries-exhausted paths.
