"""Unit tests for token validation: signature, claims, and failure modes.

Tokens are minted locally by the ``mint_token`` fixture and verified against an
in-memory JWKS document, so these tests never contact Cognito.
"""

import pytest
from pydantic import ValidationError

from auth.config import AuthSettings
from auth.exceptions import ExpiredToken, InvalidClaims, InvalidSignature, SigningKeyUnavailable
from auth.jwks import JwksClient
from auth.token import validate_token

from .conftest import (
    TEST_EMAIL,
    TEST_ROLE,
    TEST_SUB,
    TEST_TENANT_ID,
    RsaKeyPair,
    TokenFactory,
    generate_key_pair,
)


async def test_valid_token_returns_current_user(
    mint_token: TokenFactory, auth_settings: AuthSettings, jwks_client: JwksClient
) -> None:
    """Acceptance criteria 1 and 4: a valid token yields the typed caller."""
    user = await validate_token(mint_token(), settings=auth_settings, jwks_client=jwks_client)

    assert user.sub == TEST_SUB
    assert user.email == TEST_EMAIL
    assert user.tenant_id == TEST_TENANT_ID
    assert user.role == TEST_ROLE


async def test_current_user_is_immutable(
    mint_token: TokenFactory, auth_settings: AuthSettings, jwks_client: JwksClient
) -> None:
    """The identity cannot be reassigned by downstream code."""
    user = await validate_token(mint_token(), settings=auth_settings, jwks_client=jwks_client)

    with pytest.raises(ValidationError):
        user.tenant_id = "tenant-other"


async def test_expired_token_raises_expired_token(
    mint_token: TokenFactory, auth_settings: AuthSettings, jwks_client: JwksClient
) -> None:
    """Acceptance criterion 2: an elapsed ``exp`` is rejected as expired."""
    token = mint_token(lifetime_seconds=-60)

    with pytest.raises(ExpiredToken):
        await validate_token(token, settings=auth_settings, jwks_client=jwks_client)


async def test_token_signed_by_unpublished_key_raises_invalid_signature(
    mint_token: TokenFactory,
    auth_settings: AuthSettings,
    jwks_client: JwksClient,
    rogue_key_pair: RsaKeyPair,
) -> None:
    """Acceptance criterion 3: a forged signature under a known kid is rejected."""
    token = mint_token(key_pair=rogue_key_pair)

    with pytest.raises(InvalidSignature):
        await validate_token(token, settings=auth_settings, jwks_client=jwks_client)


async def test_wrong_audience_raises_invalid_claims(
    mint_token: TokenFactory, auth_settings: AuthSettings, jwks_client: JwksClient
) -> None:
    """A token minted for another app client is rejected."""
    token = mint_token(overrides={"aud": "some-other-app-client"})

    with pytest.raises(InvalidClaims):
        await validate_token(token, settings=auth_settings, jwks_client=jwks_client)


async def test_missing_audience_raises_invalid_claims(
    mint_token: TokenFactory, auth_settings: AuthSettings, jwks_client: JwksClient
) -> None:
    """An absent ``aud`` claim is a failure, not a skipped check."""
    token = mint_token(remove=["aud"])

    with pytest.raises(InvalidClaims):
        await validate_token(token, settings=auth_settings, jwks_client=jwks_client)


async def test_wrong_issuer_raises_invalid_claims(
    mint_token: TokenFactory, auth_settings: AuthSettings, jwks_client: JwksClient
) -> None:
    """A token from another user pool is rejected."""
    token = mint_token(overrides={"iss": "https://cognito-idp.us-east-1.amazonaws.com/us-east-1_OTHERPOOL"})

    with pytest.raises(InvalidClaims):
        await validate_token(token, settings=auth_settings, jwks_client=jwks_client)


async def test_missing_expiry_raises_invalid_claims(
    mint_token: TokenFactory, auth_settings: AuthSettings, jwks_client: JwksClient
) -> None:
    """A token without ``exp`` never becomes valid."""
    token = mint_token(remove=["exp"])

    with pytest.raises(InvalidClaims, match="exp"):
        await validate_token(token, settings=auth_settings, jwks_client=jwks_client)


async def test_access_token_is_rejected(
    mint_token: TokenFactory, auth_settings: AuthSettings, jwks_client: JwksClient
) -> None:
    """Only ID tokens are accepted, per ``token_use``."""
    token = mint_token(overrides={"token_use": "access"})

    with pytest.raises(InvalidClaims, match=r"Token use is 'access'"):
        await validate_token(token, settings=auth_settings, jwks_client=jwks_client)


@pytest.mark.parametrize("claim", ["sub", "email", "custom:tenant_id", "custom:role"])
async def test_missing_required_claim_raises_invalid_claims(
    mint_token: TokenFactory,
    auth_settings: AuthSettings,
    jwks_client: JwksClient,
    claim: str,
) -> None:
    """Every claim the API depends on is required."""
    token = mint_token(remove=[claim])

    with pytest.raises(InvalidClaims, match=claim):
        await validate_token(token, settings=auth_settings, jwks_client=jwks_client)


async def test_blank_tenant_claim_raises_invalid_claims(
    mint_token: TokenFactory, auth_settings: AuthSettings, jwks_client: JwksClient
) -> None:
    """An empty tenant id would break tenant isolation, so it is refused."""
    token = mint_token(overrides={"custom:tenant_id": ""})

    with pytest.raises(InvalidClaims, match="custom:tenant_id"):
        await validate_token(token, settings=auth_settings, jwks_client=jwks_client)


async def test_unknown_kid_raises_signing_key_unavailable(
    mint_token: TokenFactory,
    auth_settings: AuthSettings,
    jwks_client: JwksClient,
) -> None:
    """A token signed with a key that is not published cannot be verified."""
    token = mint_token(key_pair=generate_key_pair("unpublished-key"))

    with pytest.raises(SigningKeyUnavailable, match="unpublished-key"):
        await validate_token(token, settings=auth_settings, jwks_client=jwks_client)


@pytest.mark.parametrize(
    "token",
    [
        pytest.param("not-a-jwt", id="not-a-jwt"),
        pytest.param("", id="empty"),
        pytest.param("aaa.bbb.ccc", id="garbage-segments"),
    ],
)
async def test_malformed_token_raises_invalid_signature(
    auth_settings: AuthSettings, jwks_client: JwksClient, token: str
) -> None:
    """A token whose header cannot be read is rejected before key lookup."""
    with pytest.raises(InvalidSignature):
        await validate_token(token, settings=auth_settings, jwks_client=jwks_client)
