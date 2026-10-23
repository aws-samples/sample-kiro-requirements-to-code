"""Cognito ID token verification and claim extraction.

Verification steps, in order:

1. Read the unverified header to find the ``kid`` and resolve the matching
   public key from the cached JWKS document.
2. Verify the RS256 signature and the ``exp``, ``aud``, and ``iss`` claims.
3. Confirm ``token_use`` is ``"id"``, so access tokens (which carry no email or
   custom attributes) cannot be swapped in.
4. Extract ``sub``, ``email``, ``custom:tenant_id``, and ``custom:role`` into a
   :class:`~auth.models.CurrentUser`.

Each failure mode raises its own exception so callers, logs, and the RFC 7807
responses can distinguish them.

The JOSE implementation is PyJWT (``docs/decisions/0001-jwt-library-choice.md``,
tracked as DEV-001). PyJWT's exception hierarchy is mapped onto the exceptions in
:mod:`auth.exceptions` so nothing library-specific escapes this module.
"""

from collections.abc import Mapping
from typing import Any, Final

import jwt
from jwt.exceptions import (
    DecodeError,
    ExpiredSignatureError,
    InvalidAudienceError,
    InvalidIssuerError,
    InvalidKeyError,
    InvalidSignatureError,
    InvalidTokenError,
    MissingRequiredClaimError,
    PyJWKError,
    PyJWTError,
)

from auth.config import AuthSettings, get_auth_settings
from auth.exceptions import ExpiredToken, InvalidClaims, InvalidSignature
from auth.jwks import JsonWebKey, JwksClient, get_jwks_client
from auth.models import CurrentUser

SIGNING_ALGORITHM: Final[str] = "RS256"
"""The algorithm Cognito uses to sign user pool tokens."""

ALLOWED_ALGORITHMS: Final[tuple[str, ...]] = (SIGNING_ALGORITHM,)
"""Allow-list passed to :func:`jwt.decode`. Anything else, ``alg: none`` included, is refused."""

REQUIRED_CLAIMS: Final[tuple[str, ...]] = ("exp", "aud", "iss", "sub", "token_use")
"""Claims :func:`jwt.decode` must find, passed as its ``require`` option.

Passing ``audience`` and ``issuer`` already makes a missing ``aud`` or ``iss`` an
error, so those two entries are redundant but stated for completeness. ``exp``,
``sub``, and ``token_use`` are not: without ``require`` PyJWT treats a token with
no ``exp`` as non-expiring, and it never inspects ``sub`` or ``token_use``.
"""

EXPECTED_TOKEN_USE: Final[str] = "id"  # noqa: S105 - a claim value, not a credential
"""Only ID tokens carry the email and custom attributes this API needs."""

CLAIM_TENANT_ID: Final[str] = "custom:tenant_id"
CLAIM_ROLE: Final[str] = "custom:role"


async def validate_token(
    token: str,
    *,
    settings: AuthSettings | None = None,
    jwks_client: JwksClient | None = None,
) -> CurrentUser:
    """Verify a Cognito ID token and return the caller it identifies.

    Args:
        token: Raw JWT taken from the ``Authorization: Bearer`` header.
        settings: Cognito settings override. Defaults to the process settings.
        jwks_client: JWKS client override. Defaults to the shared client.

    Returns:
        The validated caller identity.

    Raises:
        ExpiredToken: If the ``exp`` claim has passed.
        InvalidSignature: If the signature does not verify, or the token is
            malformed to the point that no signature check is possible.
        InvalidClaims: If a required claim is missing or holds an unexpected
            value (wrong audience, wrong issuer, or wrong ``token_use``).
        SigningKeyUnavailable: If no signing key can be resolved for the token.
    """
    active_settings = get_auth_settings() if settings is None else settings
    client = get_jwks_client() if jwks_client is None else jwks_client

    signing_key = await client.get_signing_key(_read_key_id(token))
    claims = _decode(token, signing_key, active_settings)
    _verify_claims(claims, active_settings)
    return _build_current_user(claims)


def _read_key_id(token: str) -> str:
    """Return the ``kid`` from the unverified JWT header.

    The header is read before any signature check, so nothing from it is
    trusted beyond selecting which published public key to verify against.

    Args:
        token: Raw JWT.

    Returns:
        The key id.

    Raises:
        InvalidSignature: If the header cannot be parsed or carries no ``kid``.
    """
    try:
        header = jwt.get_unverified_header(token)
    except PyJWTError as exc:
        # Covers DecodeError (too few segments, undecodable header) and the
        # InvalidTokenError PyJWT raises when `kid` is present but not a string.
        raise InvalidSignature("Token header could not be parsed.") from exc

    kid = header.get("kid")
    if not isinstance(kid, str) or not kid:
        raise InvalidSignature("Token header does not identify a signing key.")
    return kid


def _verification_key(signing_key: JsonWebKey) -> jwt.PyJWK:
    """Turn a JWKS entry into a key object PyJWT can verify with.

    ``algorithm`` is supplied by this module instead of being read from the JWK's
    own ``alg`` member, so the algorithm used to verify is decided here and never
    taken from the fetched document.

    Args:
        signing_key: JWK resolved from the token's ``kid``.

    Returns:
        The key wrapped for :func:`jwt.decode`.

    Raises:
        InvalidSignature: If the JWK cannot be turned into a usable public key.
    """
    try:
        return jwt.PyJWK(signing_key, algorithm=SIGNING_ALGORITHM)
    except (PyJWKError, InvalidKeyError) as exc:
        raise InvalidSignature("Signing key could not be used to verify the token.") from exc


def _decode(token: str, signing_key: JsonWebKey, settings: AuthSettings) -> dict[str, Any]:
    """Verify the signature and the registered claims.

    Args:
        token: Raw JWT.
        signing_key: JWK resolved from the token's ``kid``.
        settings: Cognito settings supplying the expected audience and issuer.

    Returns:
        The decoded claim set.

    Raises:
        ExpiredToken: If the ``exp`` claim has passed.
        InvalidClaims: If ``aud`` or ``iss`` do not match, or a required claim
            is absent.
        InvalidSignature: If the signature does not verify, the token is signed
            with a disallowed algorithm, or the key is unusable.
    """
    try:
        claims: dict[str, Any] = jwt.decode(
            token,
            _verification_key(signing_key),
            algorithms=list(ALLOWED_ALGORITHMS),
            audience=settings.app_client_id,
            issuer=settings.issuer,
            options={"require": list(REQUIRED_CLAIMS)},
            # Cognito ID tokens carry at_hash, which can only be checked when the
            # matching access token is presented too. It is not, here. PyJWT does
            # not inspect at_hash at all, so there is nothing to switch off.
        )
    except ExpiredSignatureError as exc:
        raise ExpiredToken("Token has expired.") from exc
    except (InvalidAudienceError, InvalidIssuerError, MissingRequiredClaimError) as exc:
        raise InvalidClaims(f"Token claims are invalid: {exc}") from exc
    except (InvalidSignatureError, DecodeError, InvalidTokenError) as exc:
        # InvalidSignatureError and DecodeError are subclasses of
        # InvalidTokenError; they are named so the mapping is readable rather
        # than inferred. InvalidTokenError also covers InvalidAlgorithmError,
        # which is what rejects a token whose header asks for `alg: none`.
        raise InvalidSignature("Token signature could not be verified.") from exc
    return claims


def _verify_claims(claims: Mapping[str, Any], settings: AuthSettings) -> None:
    """Re-assert the claim rules that matter most, independently of the library.

    :func:`jwt.decode` already enforces ``exp``, ``aud``, ``iss``, and the
    :data:`REQUIRED_CLAIMS` list, so most of this is duplication. That is the
    point: these checks deliberately do not rely on library behaviour. Keeping
    them here means the rules this API actually depends on are asserted in code
    we own, so a future library swap, a default that shifts between releases, or
    an option passed wrongly cannot quietly widen what gets accepted.

    ``token_use`` is the exception rather than a duplicate — it is Cognito-specific
    and no JOSE library knows to look at it.

    Args:
        claims: Decoded claim set.
        settings: Cognito settings supplying the expected audience.

    Raises:
        InvalidClaims: If ``exp`` or ``aud`` is missing, ``aud`` does not match
            the app client id, or ``token_use`` is not ``"id"``.
    """
    if "exp" not in claims:
        raise InvalidClaims("Token is missing required claim 'exp'.")

    if claims.get("aud") != settings.app_client_id:
        raise InvalidClaims("Token audience does not match the app client id.")

    token_use = claims.get("token_use")
    if token_use != EXPECTED_TOKEN_USE:
        raise InvalidClaims(f"Token use is '{token_use}', expected '{EXPECTED_TOKEN_USE}'.")


def _build_current_user(claims: Mapping[str, Any]) -> CurrentUser:
    """Map verified claims onto :class:`~auth.models.CurrentUser`.

    Args:
        claims: Verified claim set.

    Returns:
        The caller identity.

    Raises:
        InvalidClaims: If any required claim is missing or not a non-empty string.
    """
    return CurrentUser(
        sub=_require_string_claim(claims, "sub"),
        email=_require_string_claim(claims, "email"),
        tenant_id=_require_string_claim(claims, CLAIM_TENANT_ID),
        role=_require_string_claim(claims, CLAIM_ROLE),
    )


def _require_string_claim(claims: Mapping[str, Any], name: str) -> str:
    """Return a claim that must be present as a non-empty string.

    Args:
        claims: Verified claim set.
        name: Claim name.

    Returns:
        The claim value.

    Raises:
        InvalidClaims: If the claim is absent, empty, or not a string.
    """
    value = claims.get(name)
    if not isinstance(value, str) or not value:
        raise InvalidClaims(f"Token is missing required claim '{name}'.")
    return value
