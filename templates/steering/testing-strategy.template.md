---
inclusion: fileMatch
fileMatchPattern: ["tests/**", "**/*_test.*", "**/*.test.*", "**/conftest.py"]
---

# Testing Strategy

## Layers

| Layer | Scope | Runner | Runs in |
|-------|-------|--------|---------|
| Unit | One function or class, no I/O | `[UNIT-TEST-COMMAND]` | Pre-commit + CI, every PR |
| Integration | Service against real [DEPENDENCY-LIST] | `[INTEGRATION-TEST-COMMAND]` | CI on PR |
| End-to-end | Deployed [ENV-NAME] through the public interface | `[E2E-TEST-COMMAND]` | Post-deploy to [ENV-NAME] |

Keep the pyramid weighted toward unit tests. An integration test that only re-checks branch logic already covered by a unit test buys latency, not confidence.

## Layout and Naming

- Tests mirror source paths: `src/[MODULE]/[FILE]` → `tests/unit/[MODULE]/test_[FILE]`. Kiro then knows where a new test goes.
- Test name states the behaviour: `test_[UNIT]_[CONDITION]_[EXPECTED-RESULT]`. No `test_1`, no `test_it_works`.
- Shared fixtures in `[FIXTURE-FILE]` at the narrowest scope that works. Module-scoped state that leaks between tests is the usual cause of order-dependent failures.
- Each test asserts one behaviour. Multiple assertions are fine when they describe the same outcome.

## What to Mock

| Dependency | Approach | Why |
|-----------|----------|-----|
| Cloud SDK calls | [CLOUD-MOCK-TOOL] | Fast, no credentials needed in unit runs |
| Database | Real [DATABASE] via [CONTAINER-TOOL] in integration | [WHY-REAL-DB-MATTERS] |
| Third-party HTTP | [HTTP-MOCK-TOOL] with recorded fixtures | [VENDOR-CONSTRAINT] |
| Time and randomness | Injected [CLOCK-ABSTRACTION] | Deterministic tests |
| Your own modules | Do not mock | Mocking internals tests the mock, not the code |

## Required Coverage

- Floor: [COVERAGE-PERCENT]% on `services/` and `repositories/`, enforced by `[COVERAGE-COMMAND]`. Generated code and [EXCLUDED-PATHS] are excluded in `[COVERAGE-CONFIG]`.
- Every acceptance criterion in the story maps to at least one named test. Traceability is the point: a reviewer should find the test from the criterion.
- Every bug fix ships with a test that fails without the fix.
- Error paths are tested, not just happy paths — include [PRIORITY-FAILURE-MODES].

## Test Data

- Build fixtures with [FACTORY-APPROACH]; no shared mutable global fixtures.
- Never use production data or real [SENSITIVE-DATA-CLASS] in tests. Synthetic values only.
- Integration tests create and tear down their own [ISOLATION-UNIT] so parallel runs do not collide.

## Gates

Tests must pass before a story task is checked off — enforced by the `test-after-task` hook in `.kiro/hooks/`. Flaky tests get quarantined and fixed within [FLAKE-SLA], never retried in CI to green.
