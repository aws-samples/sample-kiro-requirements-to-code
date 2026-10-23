---
inclusion: always
---

# Coding Standards

## Python (Lambda Functions)

### Project Structure
```
src/
├── functions/
│   ├── ingest/
│   │   ├── handler.py         # Lambda handler
│   │   ├── validator.py       # Schema validation logic
│   │   └── requirements.txt   # Function-specific deps
│   ├── transform/
│   │   ├── handler.py
│   │   └── requirements.txt
│   └── deliver/
│       ├── handler.py
│       └── requirements.txt
├── layers/
│   └── common/
│       └── python/
│           ├── models.py      # Shared Pydantic models
│           ├── config.py      # Environment config
│           └── responses.py   # API envelope + RFC 7807 helpers
└── schemas/
    └── *.json                 # JSON Schema definitions
```

The tree shows the PI 1 target state: `validator.py` arrives with story E2, and
`transform/` / `deliver/` with Feature 201. Only `ingest/` exists today.

### Style
- PEP 8 enforced by `ruff`.
- Line length: 120 characters.
- Type hints mandatory on all function signatures.
- Docstrings: Google style.

### Lambda Handler Pattern
```python
from aws_lambda_powertools import Logger, Tracer, Metrics
from aws_lambda_powertools.utilities.typing import LambdaContext

logger = Logger()
tracer = Tracer()
metrics = Metrics()

@logger.inject_lambda_context
@tracer.capture_lambda_handler
@metrics.log_metrics
def handler(event: dict, context: LambdaContext) -> dict:
    """Brief description of what this function does."""
    # Implementation
    return {"statusCode": 200, "body": result}
```

### Naming
| Item | Convention | Example |
|------|-----------|---------|
| Files | snake_case | `event_validator.py` |
| Functions | snake_case | `validate_schema()` |
| Classes | PascalCase | `EventProcessor` |
| Constants | UPPER_SNAKE | `MAX_BATCH_SIZE` |
| Lambda functions | kebab-case (Terraform) | `streamprocess-dev-ingest-api` |

### Error Handling
- Catch specific exceptions, never bare `except`.
- Log errors with full context (event_id, source, error details).
- Return structured error responses from API handlers.
- Let Lambda retry handle transient failures (configured in Terraform).

### Testing
- `pytest`; AWS calls are stubbed at the client boundary via fixtures (see `tests/functions/ingest/conftest.py`). Add `moto` to the dev extra only when a test needs a fuller service fake.
- Test directory mirrors src structure: `tests/functions/ingest/test_handler.py`
- Test each Lambda handler with valid events, invalid events, and error conditions.
- Integration tests use LocalStack or deploy to a test account.

## Terraform

### Module Layout
```
infra/terraform/modules/<module>/
├── main.tf
├── variables.tf
├── outputs.tf
├── versions.tf
└── README.md
```

### Naming
- Resources: `${var.name_prefix}-<resource-purpose>` 
- Lambda: `${var.name_prefix}-<function-name>`
- S3 buckets: `${var.name_prefix}-<purpose>-${data.aws_caller_identity.current.account_id}`

### Pipeline Configuration
Pipelines are defined as YAML config files:
```yaml
# pipelines/order-events.yaml
name: order-events
source: api
schema: schemas/order-event.json
steps:
  - name: validate
    function: validate-order
  - name: enrich
    function: enrich-customer-data
  - name: transform
    function: normalize-order
destination:
  type: s3
  format: parquet
  partition_by: [date, source]
```

## Git Conventions

- Branch: `story/<tracker-id>-<slug>`
- Commits: conventional (`feat:`, `fix:`, `infra:`, `docs:`)
- Trailer: `Work-Item: <tracker-id>`
- PR title: `[<id>] Short description`
- Squash merge to main
