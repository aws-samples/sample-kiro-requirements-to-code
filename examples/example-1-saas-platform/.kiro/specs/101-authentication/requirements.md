# Requirements — Authentication & Authorization (Feature 101)

**Parent Epic:** Epic 1 — User & Tenant Management
**PI:** PI-1 · **Effort:** 14 PD · **Owners:** Alice, Bob

## Feature Intent

Implement secure user authentication using AWS Cognito and role-based access control that enforces tenant isolation across all API endpoints. This is the foundational security layer that all other features depend on.

## In Scope (PI 1)

- Cognito User Pool with custom attributes (tenant_id, role)
- OAuth2 Authorization Code + PKCE flow
- JWT token validation middleware for FastAPI
- Role-based access control (Admin, Manager, Member, Viewer)
- Tenant isolation middleware (extract tenant from JWT, enforce on all queries)
- Terraform module for Cognito infrastructure
- Integration tests for auth flows

## Out of Scope (PI 1)

- Social login (Google, GitHub) — PI 2
- Multi-factor authentication — PI 2
- SSO federation with customer IdPs — PI 2
- Self-service password reset UI — PI 2 (API endpoint only in PI 1)

## Requirements Traceability

| Req | Description | PRD Section | Stories (PD) |
|-----|-------------|-------------|--------------|
| R1 | Cognito User Pool + custom attributes + Terraform | §Security, §Tech | A1 (4) |
| R2 | JWT validation middleware for FastAPI | §Security | A2 (3) |
| R3 | RBAC with four roles enforced on every endpoint | §Security, §Users | A3 (4) |
| R4 | Tenant isolation — JWT claim → query filter | §Security, §Epic 1 | A4 (3) |

**Total effort:** 14 PD · **Stories:** 4
