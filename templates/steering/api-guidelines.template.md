---
inclusion: fileMatch
fileMatchPattern: ["src/api/**", "src/**/routes/**", "src/**/handlers/**"]
---

# API Guidelines

Applies to every externally reachable endpoint. Internal-only calls follow the same shape so an endpoint can be exposed later without a rewrite.

## URL and Versioning

| Rule | Value |
|------|-------|
| Base path | `/api/v[MAJOR]/` |
| Resource naming | Plural, [PATH-CASE-CONVENTION] (`/api/v1/[EXAMPLE-RESOURCE]`) |
| Nesting depth | Two levels max; deeper relations use query filters |
| Breaking change | New major path. Never mutate a released version, because [CLIENT-UPGRADE-CONSTRAINT] |
| Deprecation | `Deprecation` and `Sunset` headers, [DEPRECATION-WINDOW] before removal |

## Methods and Status Codes

| Action | Method | Success |
|--------|--------|---------|
| List | GET | 200 |
| Read | GET | 200 |
| Create | POST | 201 + `Location` header |
| Full update | PUT | 200 |
| Partial update | PATCH | 200 |
| Delete | DELETE | 204 |

Use 400, 401, 403, 404, 409, 422, and 429 deliberately. A 500 means the service is at fault — never use it for rejected input.

## Errors

Every error body uses [ERROR-FORMAT] (e.g. RFC 7807 Problem Details) so clients parse one shape:

```json
{
  "type": "[ERROR-TYPE-URI]",
  "title": "[SHORT-SUMMARY]",
  "status": 422,
  "detail": "[WHAT-THE-CALLER-SHOULD-FIX]",
  "instance": "[REQUEST-ID]"
}
```

`instance` carries the correlation ID from `observability-guidelines.md`, so a caller report maps straight to logs. Never return stack traces or internal identifiers.

## Collections

- Pagination is [PAGINATION-STYLE] with `?[PAGE-PARAM]=&limit=`; default limit [DEFAULT-LIMIT], hard cap [MAX-LIMIT].
- Envelope: `{ "data": [...], "pagination": { "[NEXT-FIELD]": "..." } }`. Bare arrays cannot carry metadata later.
- Filtering via explicit query params ([FILTER-PARAM-EXAMPLES]) validated against an allowlist. Sorting via `?sort=[FIELD]&order=asc|desc` on [SORTABLE-FIELDS] only, since unindexed sorts scan [DATA-STORE].

## Contract and Safety

- [API-SPEC-FORMAT] is the source of truth at `[SPEC-FILE-PATH]`. Update it in the same PR; the `api-contract-check` hook flags drift in conversation (it advises — CI is the gate).
- Auth on every route by default, [AUTH-MECHANISM] verified before handler logic. Public routes are an explicit allowlist in `[ALLOWLIST-LOCATION]`.
- POST and PATCH accept `Idempotency-Key`, retained [IDEMPOTENCY-WINDOW], so client retries cannot double-write.
- Rate limit at [RATE-LIMIT-VALUE] per [RATE-LIMIT-SCOPE], returning 429 with `Retry-After`.
- Timestamps are UTC ISO 8601; money is minor units plus currency code. No floats for money.
