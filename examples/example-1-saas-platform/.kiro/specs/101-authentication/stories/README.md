# Stories — Authentication & Authorization (Feature 101)

## Conventions

- One file per story
- File name: `<ref>-<trackerId>-<slug>.md`
- Ref prefix: `A` (for Authentication)
- Front-matter drives tracker sync
- Body splits at `## Acceptance Criteria` for tracker field mapping

## Stories in This Feature

| Ref | Title | Sprint | Owner | Effort | Status |
|-----|-------|--------|-------|--------|--------|
| A1 | Cognito User Pool Terraform Module | S1 | alice | 4 PD | Done |
| A2 | JWT Validation Middleware | S1 | bob | 3 PD | Done |
| A3 | Role-Based Access Control | S2 | alice | 4 PD | New |
| A4 | Tenant Isolation Middleware | S2 | bob | 3 PD | New |

## Dependency Graph

```
A1 (Cognito Terraform)
  └── A2 (JWT Middleware)
        ├── A3 (RBAC)
        └── A4 (Tenant Isolation)
```
