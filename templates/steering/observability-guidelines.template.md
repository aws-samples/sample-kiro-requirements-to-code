---
inclusion: fileMatch
fileMatchPattern: "src/**"
---

# Observability Guidelines

Instrumentation ships with the feature, not in a follow-up story. A story is not done if its failure mode is invisible in [DASHBOARD-OR-TOOL].

## Logging

- Structured JSON only, via the shared logger in `src/[SHARED-MODULE]/`. Text logs cannot be queried in [LOG-QUERY-TOOL].
- Required fields on every line:

| Field | Source | Purpose |
|-------|--------|---------|
| `timestamp` | Logger | UTC ISO 8601 |
| `level` | Logger | Filtering |
| `service` | [SERVICE-NAME-ENV-VAR] | Which component emitted it |
| `correlation_id` | `[CORRELATION-HEADER]` or generated at edge | Stitches one request across services |
| `[SCOPE-FIELD]` | Verified token claim | Scopes queries to one [TENANT-OR-SCOPE] |
| `event` | Call site | Stable machine-readable name |

- Levels: ERROR = someone must act; WARN = degraded but handled; INFO = state change worth an audit trail; DEBUG = off in [PROD-ENV-NAME].
- Never log [SENSITIVE-DATA-CLASS], credentials, bearer values, or full payloads. See `security-guidelines.md`.
- Retention [LOG-RETENTION] in [LOG-DESTINATION].

## Tracing

- [TRACING-STACK] on every entry point and every outbound call to [TRACED-DEPENDENCIES].
- Propagate the trace context across [ASYNC-BOUNDARIES]. A broken trace at a queue hop hides the slowest hop.
- Annotate spans with [SPAN-ANNOTATIONS]. No sensitive values in span attributes — they are stored like logs.
- Sampling: [SAMPLING-RATE], with errors always sampled.

## Metrics

| Metric | Type | Dimensions |
|--------|------|-----------|
| `[NAMESPACE].[OPERATION].count` | Counter | [DIMENSION-LIST] |
| `[NAMESPACE].[OPERATION].duration` | Histogram | [DIMENSION-LIST] |
| `[NAMESPACE].[OPERATION].errors` | Counter | [DIMENSION-LIST] |
| `[BUSINESS-METRIC]` | [TYPE] | [DIMENSION-LIST] |

Keep dimension cardinality bounded — never use [HIGH-CARDINALITY-EXAMPLE] as a dimension, because [COST-OR-LIMIT-REASON].

## Alerts

Alert on symptoms users feel, not on causes. Every alert names an owner and a runbook, or it gets deleted.

| Condition | Threshold | Severity | Runbook |
|-----------|-----------|----------|---------|
| [USER-FACING-SYMPTOM] | [THRESHOLD] over [WINDOW] | [SEVERITY] | `[RUNBOOK-PATH]` |
| [SLO-BURN-CONDITION] | [THRESHOLD] | [SEVERITY] | `[RUNBOOK-PATH]` |
| [SATURATION-CONDITION] | [THRESHOLD] | [SEVERITY] | `[RUNBOOK-PATH]` |

## SLOs

| Service | Indicator | Objective |
|---------|-----------|-----------|
| [SERVICE-NAME] | [LATENCY-PERCENTILE] | [TARGET] |
| [SERVICE-NAME] | Availability | [TARGET] |

Health endpoints: `[HEALTH-PATH]` for liveness (process up), `[READY-PATH]` for readiness (dependencies reachable). Keep them separate so a dependency blip does not trigger restarts.
