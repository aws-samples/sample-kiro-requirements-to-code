---
trackerId: ADO-12304
ref: A4
parent: 101
title: "Tenant Isolation Middleware — schema-per-tenant routing and data boundary enforcement"
state: New
sprint: S2
owner: bob
effort: 3
priority: 2
tags: [auth, api, database, multi-tenancy, PI1]
dependsOn: [A2]
lastSync: 2026-07-25T14:15:00Z
---

## Context

Fourth story in Feature 101. Implements the database-level tenant isolation using PostgreSQL schemas. Extracts tenant_id from the JWT (via A2's CurrentUser) and sets the connection's `search_path` to the tenant's schema, ensuring all queries are scoped.

## Goal

As a platform engineer, I want automatic tenant-scoped database connections so that application code cannot accidentally access another tenant's data.

## Scope

- FastAPI middleware that extracts tenant_id from CurrentUser
- Database connection wrapper that sets `search_path` to `tenant_{tenant_id}`
- Schema existence validation (reject if schema doesn't exist)
- Connection pool management with per-request schema switching
- Tenant schema creation utility (for onboarding, called separately)
- Integration tests proving cross-tenant isolation

## Out of Scope

- Tenant onboarding API (separate feature)
- Schema migration tooling across all tenants (follow-up)
- Connection pooler (PgBouncer) — using application-level pooling for now

## Dependencies

- Requires: A2 (CurrentUser provides tenant_id)
- Requires: Infrastructure story providing Aurora cluster (from Feature 301)
- Blocks: All data-access stories in Epic 2

## Acceptance Criteria

- **Given** a request with JWT containing `tenant_id = "alpha"`, **When** the request reaches a database query, **Then** the connection's `search_path` is set to `tenant_alpha`.
- **Given** tenant "alpha" data exists, **When** tenant "beta" makes a query, **Then** tenant "alpha" data is never visible in the results.
- **Given** a JWT with `tenant_id = "nonexistent"`, **When** the middleware resolves the schema, **Then** a 403 response is returned (tenant not provisioned).
- **Given** concurrent requests from different tenants, **When** they execute simultaneously, **Then** each connection independently maintains the correct search_path (no cross-contamination).
- **Given** the schema creation utility, **When** called with `tenant_id = "gamma"`, **Then** a new schema `tenant_gamma` is created with the standard table set.
