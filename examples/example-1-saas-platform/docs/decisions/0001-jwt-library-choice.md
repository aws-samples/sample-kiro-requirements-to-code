# ADR 0001 — PyJWT for runtime token verification

**Status:** Accepted (amended 2026-10-09, see below)
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
floor (not an API floor — do not lower it). Mint test tokens with an
**independent implementation**: the fixtures build the compact JWS by hand
(RFC 7515) and sign it with `cryptography` so the suite exercises PyJWT against
tokens it did not produce itself, which catches interoperability assumptions a
same-library round-trip would hide. (Originally this role was filled by
`python-jose` as a dev-only dependency; see the 2026-10-09 amendment.)

`src/auth/token.py` supplies the verification algorithm itself rather than
trusting the JWK's `alg` member, and maps PyJWT's exception hierarchy onto
`auth.exceptions` so nothing library-specific escapes the module. A future
library swap touches one file.

## Consequences

- One JOSE library appears in `pyproject.toml` (PyJWT, in `dependencies`). The
  `dev` extra declares `cryptography` explicitly because the test fixtures import
  it directly for key generation and token signing; the comment says why.
- The deviation from the A2 plan is recorded as DEV-001 in the feature's
  work-item map, pointing here. Design docs stay honest.
- Rollback path: the exception mapping and the single-module boundary mean
  swapping the runtime library is contained; the hand-built fixtures keep
  working as the independent token source either way.
- The fixture helper (`_mint_rs256` in `tests/unit/auth/conftest.py`) only
  signs. It does not add or validate claims, so tests that need expired, mis-
  keyed or claim-less tokens get exactly the payload they ask for.

## Amendment 2026-10-09 — python-jose removed

`python-jose` was dropped from the `dev` extra. Every released version through
3.5.0 (the latest) accepts DER-encoded asymmetric public keys as HMAC secrets,
which enables HS256 algorithm-confusion forgery when `algorithms` is not
restricted. This is PYSEC-2026-4298 / upstream issue
[mpdavis/python-jose#414](https://github.com/mpdavis/python-jose/issues/414),
an incomplete fix for CVE-2024-33663. No fixed release exists, so a version
bump was not available.

The runtime was never exposed: verification uses PyJWT with
`algorithms=["RS256"]` pinned in `src/auth/token.py`, and python-jose was only
ever used to mint tokens in tests. Rather than suppress the finding or swap in
a third JOSE library, the fixtures now sign a hand-built JWS with
`cryptography`, which was already a declared dev dependency. The original
comparison table above is kept as history; the choice of PyJWT at runtime is
unchanged.
