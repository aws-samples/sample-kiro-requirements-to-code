# Epic 1: User & Tenant Management

## Vision

Provide secure, scalable user authentication and tenant isolation that allows TaskFlow to serve multiple organizations on shared infrastructure without any data leakage between tenants.

## Capabilities

- User registration and login (email/password + social login)
- OAuth2/OIDC authentication via AWS Cognito
- Role-based access control (Admin, Manager, Member, Viewer)
- Tenant provisioning and data isolation
- User profile management
- Security audit logging

## Features

| Feature | ID | PI | Status | Stories | Effort |
|---------|----|----|--------|---------|--------|
| Authentication & Authorization | 101 | PI 1 | In Progress | 4 | 14 PD |
| User Profile Management | 102 | PI 1 | Planned | 3 | 8 PD |

## Dependencies

- Depends on: Epic 3 (Infrastructure) — needs VPC, ECS, Aurora before deployment
- Blocks: Epic 2 (Projects & Tasks) — needs auth middleware before API endpoints

## Success Metrics

- User can register and login in < 3 seconds
- Token validation adds < 10ms to request latency
- Zero cross-tenant data access in penetration testing
- Audit log captures 100% of auth events
