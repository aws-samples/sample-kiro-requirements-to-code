---
trackerId: pending
ref: E2
parent: 101
title: "Schema Validation + Dead Letter Queue — JSON Schema validation with DLQ routing"
state: New
sprint: S2
owner: dana
effort: 4
priority: 1
tags: [ingestion, validation, sqs, PI1]
dependsOn: [E1, E4]
lastSync: 1970-01-01T00:00:00Z
---

## Context

Third story in Feature 101. Adds schema validation to the ingestion Lambda (built in E1) and routes invalid events to an SQS dead-letter queue with diagnostic metadata. Schemas are stored in S3 and cached in Lambda memory.

## Goal

As a data engineer, I want events validated against registered schemas at ingestion time so that only structurally correct events enter the processing pipeline, and invalid events are captured for investigation.

## Scope

- JSON Schema validation using `jsonschema` library
- Schema storage: S3 bucket with `schemas/{source_name}/v{version}.json` key pattern
- Schema caching in Lambda memory (TTL: 5 minutes, refreshed on miss)
- Schema resolution: event header `X-Schema-Name` + `X-Schema-Version` determines which schema to apply
- DLQ (SQS): invalid events with metadata (correlation_id, source, schema_name, validation_errors, original_event)
- DLQ alarm: CloudWatch alarm when messages > 0
- Schema management API (GET /schemas, PUT /schemas/{name}/{version})

## Out of Scope

- EventBridge Schema Registry migration (PI 2)
- Schema evolution / compatibility checking (PI 2)
- Custom validation rules beyond JSON Schema (PI 2)

## Dependencies

- Requires: E1 (ingestion Lambda handler to add validation step)
- Requires: E4 (Terraform module and the SQS dead-letter queue; this story extends that module with the schema S3 bucket, the DLQ alarm, and the schema management endpoints — all listed in E4's Out of Scope)

## Acceptance Criteria

- **Given** an event with `X-Schema-Name: order-event` and `X-Schema-Version: 1`, **When** the event body matches `schemas/order-event/v1.json`, **Then** the event passes validation and proceeds to processing.
- **Given** an event that fails schema validation, **When** processed by the ingestion Lambda, **Then** the event is written to the DLQ with: correlation_id, source, schema_name, schema_version, validation_errors (array of paths + messages), original_event_body, timestamp.
- **Given** the DLQ receives a message, **When** the CloudWatch alarm evaluates, **Then** the alarm enters ALARM state within 1 minute.
- **Given** a schema file at `s3://schemas-bucket/schemas/order-event/v1.json`, **When** the Lambda loads schemas, **Then** the file is cached in memory for 5 minutes before re-fetching.
- **Given** a PUT request to `/schemas/order-event/2` with a valid JSON Schema body, **When** processed, **Then** the schema is stored in S3 at the correct key path.
- **Given** an event without `X-Schema-Name` header, **When** processed, **Then** the response is 400 with Problem Details explaining the missing header.
