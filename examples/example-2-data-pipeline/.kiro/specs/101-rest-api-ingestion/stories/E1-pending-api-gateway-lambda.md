---
trackerId: pending
ref: E1
parent: 101
title: "API Gateway + Ingestion Lambda — REST endpoint with API key auth"
state: Done
sprint: S1
owner: dana
effort: 3
priority: 1
tags: [ingestion, api, lambda, PI1]
dependsOn: []
lastSync: 1970-01-01T00:00:00Z
---

## Context

First story in Feature 101 (REST API Ingestion). Creates the HTTP endpoint that event publishers use to submit events. Authentication via API keys, basic request validation, and a placeholder Lambda that accepts and logs events.

## Goal

As an event publisher, I want a REST API endpoint so that I can submit events over HTTPS and receive immediate acknowledgment with a correlation ID.

## Scope

- API Gateway REST API with `/events` POST endpoint
- Usage plan with API key requirement
- Lambda handler: accept event, generate correlation ID (UUIDv7), log, return 202
- Request validation: require Content-Type: application/json, body not empty
- Structured JSON response: `{ "correlation_id": "...", "status": "accepted" }`
- Error responses in RFC 7807 Problem Details format
- CloudWatch log group with 14-day retention
- X-Ray tracing enabled on both API Gateway and Lambda
- Unit tests with mocked API Gateway event

## Out of Scope

- Schema validation (E2)
- Kinesis persistence (E3)
- Terraform for infrastructure (E4 — this story uses SAM/manual for initial Lambda)
- Rate limiting per source

## Dependencies

- Requires: E4 (Terraform module) for production deployment, but can develop Lambda independently
- Blocks: E2, E3 (need the Lambda handler to add validation and persistence)

## Acceptance Criteria

- **Given** a valid POST to `/events` with API key header, **When** the body is valid JSON, **Then** the response is 202 with `{ "correlation_id": "<uuid>", "status": "accepted" }`.
- **Given** a request without `x-api-key` header, **When** it hits the endpoint, **Then** API Gateway returns 403 Forbidden.
- **Given** a request with `Content-Type` other than `application/json`, **When** it hits the Lambda, **Then** the response is 415 Unsupported Media Type.
- **Given** an empty body, **When** the request reaches the Lambda, **Then** the response is 400 with Problem Details explaining the issue.
- **Given** any request, **When** processed by the Lambda, **Then** a structured JSON log entry includes correlation_id, source_ip, timestamp, and event_size_bytes.
- **Given** X-Ray is enabled, **When** a request is processed, **Then** a trace segment appears in the X-Ray console.

## Implementation Tasks

### Task 1: Lambda Function

- [x] 1.1 Create `src/functions/ingest/handler.py` — main handler with Powertools decorators
- [x] 1.2 Create `src/functions/ingest/models.py` — Pydantic models for request/response
- [x] 1.3 Create `src/functions/ingest/exceptions.py` — custom exceptions with Problem Details mapping
- [x] 1.4 Implement correlation ID generation (UUIDv7 via `uuid7` package)
- [x] 1.5 Implement request validation (content-type, non-empty body, valid JSON)
- [x] 1.6 Create `src/functions/ingest/requirements.txt` — aws-lambda-powertools, pydantic, uuid7

### Task 2: Shared Layer

- [x] 2.1 Create `src/layers/common/python/models.py` — shared event envelope model
- [x] 2.2 Create `src/layers/common/python/config.py` — environment-based config (log level, service name)
- [x] 2.3 Create `src/layers/common/python/responses.py` — RFC 7807 Problem Details helper

### Task 3: Tests

- [x] 3.1 Create `tests/functions/ingest/test_handler.py` — test valid event, missing API key, invalid content-type, empty body
- [x] 3.2 Create `tests/functions/ingest/conftest.py` — fixtures for API Gateway proxy events
- [x] 3.3 Create `tests/layers/test_responses.py` — test Problem Details formatting

### Task 4: Validation

- [x] 4.1 `ruff check src/` — no findings
- [x] 4.2 `ruff format --check src/` — passes
- [x] 4.3 `pytest tests/functions/ingest/` — all pass
- [x] 4.4 `mypy src/functions/ingest/` — no type errors
- [x] 4.5 Deploy manually to dev, test with curl — verify 202 response
