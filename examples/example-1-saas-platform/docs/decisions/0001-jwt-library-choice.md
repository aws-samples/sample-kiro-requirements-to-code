# ADR 0001 — PyJWT for runtime token verification

**Status:** Accepted
**Date:** 2026-07-20
**Story:** A2 (JWT Validation Middleware, Feature 101)
**Deviation:** DEV-001 in `.kiro/specs/101-authentication/work-item-map.yaml`

## Context

Feature 101's design (`DEC-001`) selects Cognito as the identity provider but does
not name a JOSE library for verifying its RS256 ID tokens. Story A2 was planned
assuming `python-jose` throughout — its task 5.4 mints test tokens with it — and
the implicit expectation was that the same library would verify tokens at runtime.

During implementation we compared the two candidates:

| Criterion | PyJWT | python-jose |
|-----------|-------|-------------|
| Maintenance | Active; 2.13 released with security fixes | Sporadic release cadence |
| Typing | Ships type hints; works under `mypy --strict` | Untyped |
| JWK handling | `jwt.PyJWK` lets us pin the verify algorithm ourselves | Reads `alg` from the fetched JWK |
| Security posture | 2.13 fixes CVE-2026-48526 (algorithm confusion when decoding with a raw JWK while mixed algorithm families are supported) — exactly our verification path | Historical algorithm-confusion CVEs; fixes landed slowly |

The CVE-2026-48526 fix matters here because `src/auth/token.py` verifies Cognito
tokens against keys resolved from a fetched JWKS document. An algorithm-confusion
flaw in that path is a token-forgery primitive.

## Decision

Use **PyJWT (`pyjwt[crypto]`) at runtime**, floored at `>=2.13` as a security
floor (not an API floor — do not lower it). Keep **python-jose as a dev-only
dependency**: the test fixtures mint tokens with it so the suite exercises PyJWT
against tokens produced by an independent implementation, which catches
interoperability assumptions a same-library round-trip would hide.

`src/auth/token.py` supplies the verification algorithm itself rather than
trusting the JWK's `alg` member, and maps PyJWT's exception hierarchy onto
`auth.exceptions` so nothing library-specific escapes the module. A future
library swap touches one file.

## Consequences

- Two JOSE libraries appear in `pyproject.toml` — one in `dependencies`, one in
  the `dev` extra. The comment on each says why.
- The deviation from the A2 plan is recorded as DEV-001 in the feature's
  work-item map, pointing here. Design docs stay honest.
- Rollback path: the exception mapping and the single-module boundary mean
  swapping the runtime library is contained; the python-jose-minted fixtures
  keep working as the independent token source either way.
