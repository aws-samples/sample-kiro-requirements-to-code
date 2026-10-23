---
inclusion: always
---

# Coding Standards

## Python

### Style
- Follow PEP 8. Enforced by `ruff` (linting + formatting).
- Line length: 120 characters.
- Type hints on all function signatures and return types.
- Docstrings: Google style for public functions and classes.

### Project Structure (per service)
```
src/<service-name>/
├── main.py              # FastAPI app entry, router registration
├── config.py            # Pydantic Settings for env-based config
├── dependencies.py      # FastAPI dependency injection (DB pool, auth)
├── models/              # Pydantic request/response models
├── routes/              # Route handlers grouped by resource
├── services/            # Business logic (no HTTP concepts)
├── repositories/        # Database access (raw SQL + asyncpg)
├── middleware/          # Custom middleware (tenant context, logging)
└── exceptions.py        # Custom exception classes + handlers
```

### Naming
| Item | Convention | Example |
|------|-----------|---------|
| Files | snake_case | `task_service.py` |
| Classes | PascalCase | `TaskService` |
| Functions | snake_case | `create_task()` |
| Constants | UPPER_SNAKE | `MAX_RETRY_COUNT` |
| Env vars | UPPER_SNAKE | `DATABASE_URL` |
| API routes | kebab-case | `/api/v1/task-boards` |

### Error Handling
- All exceptions inherit from a base `AppException` class.
- HTTP exceptions map to RFC 7807 Problem Details format.
- Business logic raises domain exceptions, routes translate to HTTP.
- Never catch bare `Exception` — always be specific.

### Testing
- `pytest` with `pytest-asyncio` for async tests.
- Separate directories: `tests/unit/`, `tests/integration/`, `tests/e2e/`.
- Fixtures in `conftest.py` at appropriate scope.
- Minimum 80% coverage for business logic (services, repositories).
- Integration tests use real database (testcontainers or Aurora clone).

## Terraform

- See `infra-guidelines.md` (fileMatch: infra/**) for full Terraform standards.
- Summary: modules have `main.tf`, `variables.tf`, `outputs.tf`, `versions.tf`.
- `name_prefix` pattern for all resource names.
- Required tags on every resource.

## Git

### Branching
- `main` — production-ready, protected
- `feature/<feature-slug>` — feature work
- `story/<tracker-id>-<slug>` — individual story implementation
- `fix/<issue-id>-<slug>` — bug fixes

### Commits
- Conventional commits: `feat:`, `fix:`, `chore:`, `docs:`, `infra:`
- Include work-item trailer: `Work-Item: <tracker-id>`
- Keep commits focused — one logical change per commit

### PRs
- Title: `[<tracker-id>] Short summary`
- Description: What changed, why, how to test, any deviations from design
- Squash merge to main (clean history)
- Require 1 approval + CI green before merge

## API Design

- RESTful with resource-based URLs
- Version prefix: `/api/v1/`
- JSON request/response bodies
- Standard HTTP status codes (200, 201, 204, 400, 401, 403, 404, 409, 500)
- Pagination: cursor-based (`?cursor=X&limit=N`)
- Filtering: query parameters (`?status=active&assignee=user-id`)
- Sorting: `?sort=created_at&order=desc`
- Envelope response: `{ "data": [...], "pagination": { "next_cursor": "..." } }`
