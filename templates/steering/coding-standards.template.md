---
inclusion: always
---

<!-- Context budget: keep this file under ~150 lines. It loads into EVERY conversation.
     Push stack-specific depth into fileMatch files (api-guidelines, testing-strategy). -->

# Coding Standards

## Tooling

| Concern | Rule | Rationale |
|---------|------|-----------|
| Language | [LANGUAGE] [VERSION] | [WHY-THIS-VERSION] |
| Formatter | `[FORMAT-COMMAND]`, run pre-commit | No style debate in review |
| Linter | `[LINT-COMMAND]`, blocking in CI | [WHY] |
| Line length | [MAX-LINE-LENGTH] | Matches [FORMATTER-NAME] config |
| Types | `[TYPE-CHECK-COMMAND]`, strict mode | [WHY] |

Tool config lives in `[CONFIG-FILE-PATH]`. Change the config, never inline suppressions.

## Naming

| Item | Convention | Example |
|------|-----------|---------|
| Files | [CONVENTION] | `[EXAMPLE]` |
| Classes / types | [CONVENTION] | `[EXAMPLE]` |
| Functions | [CONVENTION] | `[EXAMPLE]` |
| Constants | [CONVENTION] | `[EXAMPLE]` |
| Env vars | [CONVENTION] | `[EXAMPLE]` |
| API routes | [CONVENTION] | `[EXAMPLE]` |
| Cloud resources | `[NAME-PREFIX-PATTERN]` | `[EXAMPLE]` |

## Module Layout

Every [SERVICE-OR-MODULE] uses this shape so Kiro places new code without asking:

```
src/[MODULE-NAME]/
├── [ENTRYPOINT-FILE]     # [WHAT-LIVES-HERE]
├── config.[EXT]          # Typed config from env, no scattered env reads
├── models/               # Request/response + domain types
├── [TRANSPORT-DIR]/      # Handlers only, zero business logic
├── services/             # Business logic, transport-agnostic
├── repositories/         # Data access only
└── exceptions.[EXT]      # Error types and handlers
```

Business logic stays out of the transport layer so it is testable without [TRANSPORT-NAME].

## Error Handling

- All errors inherit `[BASE-ERROR-TYPE]` so the top-level handler can classify them.
- Services raise domain errors; the transport layer maps them to [ERROR-FORMAT].
- Catch specific error types. A broad catch hides real defects behind a [DEFAULT-STATUS] response.
- Retry only [RETRYABLE-CONDITIONS]; everything else fails fast and loud.

## Testing (Summary)

- Runner: `[TEST-COMMAND]`. Coverage floor [COVERAGE-PERCENT]% on services and repositories, enforced in CI.
- Tests mirror source paths: `src/[MODULE-NAME]/x.[EXT]` → `tests/unit/[MODULE-NAME]/test_x.[EXT]`.
- Full detail in `testing-strategy.md`, which loads when you open a test file.

## Documentation

- [DOCSTRING-STYLE] docstrings on [DOCUMENTED-SCOPE]. Explain why, not what.
- One ADR in `docs/decisions/` per non-obvious choice, linked from the story that caused it.

Branch, commit, and PR rules live in `pr-conventions.md` — attach with `#pr-conventions`.
