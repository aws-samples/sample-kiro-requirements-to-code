---
trackerId: ADO-12303
ref: A3
parent: 101
title: "Role-Based Access Control — permission enforcement via FastAPI dependencies"
state: New
sprint: S2
owner: alice
effort: 4
priority: 2
tags: [auth, api, python, PI1]
dependsOn: [A2]
lastSync: 2026-07-25T14:15:00Z
---

## Context

Third story in Feature 101. Builds on the JWT middleware (A2) to enforce role-based permissions on every API endpoint. Four roles in hierarchical order: Viewer < Member < Manager < Admin.

## Goal

As an API developer, I want a composable RBAC dependency so that I can protect any endpoint with a single line declaring the minimum required role.

## Scope

- Role hierarchy: Viewer < Member < Manager < Admin
- `require_role(minimum_role)` FastAPI dependency
- Permission denied returns 403 with Problem Details body
- Audit log entry on permission denial (structured JSON log)
- Per-endpoint role configuration via dependency injection
- Comprehensive test coverage for all role combinations

## Out of Scope

- Fine-grained resource-level permissions (e.g., "can edit only own tasks")
- Policy engine integration (Cedar/OPA) — future PI
- Role management API (Admin can assign roles via Cognito console for now)

## Dependencies

- Requires: A2 (JWT Middleware provides CurrentUser with role claim)
- Used by: All subsequent API endpoints in Epic 2

## Acceptance Criteria

- **Given** a user with role `Member`, **When** they access an endpoint requiring `Member`, **Then** access is granted.
- **Given** a user with role `Viewer`, **When** they access an endpoint requiring `Manager`, **Then** 403 is returned with Problem Details body.
- **Given** a user with role `Admin`, **When** they access any endpoint, **Then** access is always granted (Admin >= all roles).
- **Given** a permission denial, **When** the response is sent, **Then** a structured log entry is emitted with user_id, tenant_id, required_role, actual_role, endpoint.
- **Given** the `require_role` dependency, **When** applied to an endpoint like `@router.get("/", dependencies=[Depends(require_role("Manager"))])`, **Then** it enforces the role check before the handler executes.

## Implementation Tasks

<!-- Added during Sprint 2 planning — see Spec PR spec/101-rbac-sprint2-plan -->

### Task 1: Role Enumeration and Hierarchy

- [ ] 1.1 Add `Role` enum to `src/auth/models.py` — `VIEWER = "viewer"`, `MEMBER = "member"`, `MANAGER = "manager"`, `ADMIN = "admin"`
- [ ] 1.2 Add `ROLE_HIERARCHY: dict[Role, int]` to `models.py` mapping each role to an integer rank (Viewer=0, Member=1, Manager=2, Admin=3)
- [ ] 1.3 Update `CurrentUser.role` field type from `str` to `Role`
- [ ] 1.4 Update `token.py` claim extraction to parse `custom:role` into `Role`; raise `InvalidClaims` if the value is not a known role

### Task 2: `require_role` Dependency

- [ ] 2.1 Add `require_role(minimum_role: Role) -> Callable` factory function to `src/auth/dependencies.py`
- [ ] 2.2 Factory returns a FastAPI dependency function that calls `get_current_user`, then compares `current_user.role` rank against the `minimum_role` rank using `ROLE_HIERARCHY`
- [ ] 2.3 On insufficient role: emit a structured JSON log entry with fields `event="permission_denied"`, `user_id`, `tenant_id`, `required_role`, `actual_role`, `path`; then raise `AuthorizationError`
- [ ] 2.4 Export `require_role` from `src/auth/__init__.py`

### Task 3: Exception Wiring

- [ ] 3.1 Verify `AuthorizationError` maps to 403 with Problem Details body in the exception handlers registered by `register_exception_handlers()` (implemented in A2 — confirm no changes needed)
- [ ] 3.2 Add `WWW-Authenticate` header to 403 response only when the denial is due to missing authentication (not role mismatch) — confirm existing handler already does this correctly

### Task 4: Tests

- [ ] 4.1 Create `tests/unit/auth/test_rbac.py` — test each role combination: Member accessing Member endpoint (pass), Viewer accessing Manager endpoint (fail), Admin accessing any endpoint (pass), hierarchy boundary cases
- [ ] 4.2 Test audit log emission: mock the logger, verify the structured fields are present on denial
- [ ] 4.3 Test `Role` parsing in `token.py`: unknown role value raises `InvalidClaims`
- [ ] 4.4 Update `tests/unit/auth/conftest.py` — add `mint_jwt_with_role(role: Role)` fixture helper

### Task 5: Validation

- [ ] 5.1 `ruff check` — no findings
- [ ] 5.2 `ruff format --check` — passes
- [ ] 5.3 `pytest tests/unit/auth/` — all pass
- [ ] 5.4 `mypy src/auth/` — no type errors
- [ ] 5.5 Acceptance criteria verified manually: all five Given/When/Then scenarios exercised
