---
trackerId: ADO-12302
ref: A2
parent: 101
title: "JWT Validation Middleware — token verification, claims extraction, FastAPI integration"
state: Done
sprint: S1
owner: bob
effort: 3
priority: 2
tags: [auth, api, python, PI1]
dependsOn: [A1]
lastSync: 2026-07-25T14:15:00Z
---

## Context

Second story in Feature 101. Implements the FastAPI middleware that validates JWT tokens issued by Cognito (provisioned in A1) and extracts user claims for downstream use by RBAC (A3) and tenant isolation (A4).

## Goal

As a backend developer, I want a reusable JWT validation middleware so that every API endpoint automatically verifies authentication and provides type-safe access to user claims.

## Scope

- FastAPI dependency that validates Bearer tokens from the Authorization header
- JWKS fetching and caching from Cognito User Pool
- Token signature verification (RS256)
- Claims extraction: sub, email, custom:tenant_id, custom:role
- Typed `CurrentUser` model available via dependency injection
- Proper error responses (401 Unauthorized, 403 Forbidden)
- Unit tests with mocked JWKS
- Integration test against real Cognito (optional, CI-gated)

## Out of Scope

- Role enforcement (A3)
- Tenant database routing (A4)
- Token refresh logic (client responsibility)
- Rate limiting on auth failures (future)

## Dependencies

- Requires: A1 (Cognito User Pool must exist for JWKS URL)
- Blocks: A3 (RBAC), A4 (Tenant Isolation)

## Acceptance Criteria

- **Given** a valid JWT from Cognito, **When** a request hits any protected endpoint, **Then** the middleware validates the signature, expiry, and audience, and the request proceeds.
- **Given** an expired JWT, **When** a request hits a protected endpoint, **Then** the middleware returns 401 with a Problem Details JSON body.
- **Given** a JWT with an invalid signature, **When** a request hits a protected endpoint, **Then** the middleware returns 401.
- **Given** a valid JWT with `custom:tenant_id = "tenant-abc"`, **When** the route handler accesses `current_user.tenant_id`, **Then** it receives `"tenant-abc"`.
- **Given** the JWKS endpoint is temporarily unavailable, **When** the middleware needs to validate a token, **Then** it uses cached keys (TTL: 1 hour) and does not fail.
- **Given** the middleware is applied, **When** no Authorization header is present, **Then** the response is 401 with `WWW-Authenticate: Bearer`.

## Implementation Tasks

### Task 1: Project Structure

- [x] 1.1 Create `src/auth/` package with `__init__.py`
- [x] 1.2 Create `src/auth/config.py` — Pydantic Settings for Cognito config (user_pool_id, region, app_client_id)
- [x] 1.3 Create `src/auth/models.py` — `CurrentUser` Pydantic model (sub, email, tenant_id, role)

### Task 2: JWKS Client

- [x] 2.1 Create `src/auth/jwks.py` — async JWKS fetcher with in-memory TTL cache (1 hour)
- [x] 2.2 Implement key lookup by `kid` from JWT header
- [x] 2.3 Handle JWKS fetch failures gracefully (use cached keys, log warning)

### Task 3: Token Validation

- [x] 3.1 Create `src/auth/token.py` — `validate_token(token: str) -> CurrentUser`
- [x] 3.2 Verify signature using cached JWKS (RS256)
- [x] 3.3 Verify claims: exp, aud (matches app_client_id), iss (matches user pool URL), token_use = "id"
- [x] 3.4 Extract custom claims: tenant_id, role
- [x] 3.5 Raise typed exceptions for each failure mode (ExpiredToken, InvalidSignature, InvalidClaims)

### Task 4: FastAPI Integration

- [x] 4.1 Create `src/auth/dependencies.py` — `get_current_user` FastAPI Depends function
- [x] 4.2 Extract Bearer token from Authorization header
- [x] 4.3 Call `validate_token`, return `CurrentUser` on success
- [x] 4.4 Create exception handlers: map auth exceptions → 401/403 Problem Details responses
- [x] 4.5 Create `src/auth/exceptions.py` — AuthenticationError, AuthorizationError

### Task 5: Tests

- [x] 5.1 Unit tests for JWKS cache (mock HTTP, verify TTL behavior)
- [x] 5.2 Unit tests for token validation (valid token, expired, bad signature, missing claims)
- [x] 5.3 Unit tests for FastAPI dependency (mock validate_token, verify response codes)
- [x] 5.4 Create test fixtures: generate RS256 key pair, mint test JWTs with `python-jose`

### Task 6: Validation

- [x] 6.1 `ruff check` — no findings
- [x] 6.2 `ruff format --check` — passes
- [x] 6.3 `pytest tests/unit/auth/` — all pass
- [x] 6.4 `mypy src/auth/` — no type errors
