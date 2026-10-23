"""Fixtures for the auth unit tests.

Everything is generated in-process: RSA key pairs are created at test runtime,
tokens are minted locally, and the JWKS document is a plain dict served through
an :class:`httpx.MockTransport`. No key material is stored in the repository and
no test touches the network or AWS.
"""

import base64
import time
from collections.abc import AsyncIterator, Iterable, Mapping
from dataclasses import dataclass
from typing import Any, Protocol

import httpx
import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from jose import jwt

from auth.config import AuthSettings
from auth.jwks import JwksClient

TEST_USER_POOL_ID = "us-east-1_TESTPOOL1"
TEST_REGION = "us-east-1"
TEST_APP_CLIENT_ID = "1example23client45id67"
TEST_SIGNING_KID = "taskflow-test-key-1"
TEST_TENANT_ID = "tenant-abc"
TEST_SUB = "11111111-2222-3333-4444-555555555555"
TEST_EMAIL = "dana@tenant-abc.example.com"
TEST_ROLE = "member"

RSA_KEY_SIZE = 2048
RSA_PUBLIC_EXPONENT = 65537


@dataclass(frozen=True)
class RsaKeyPair:
    """An RSA key pair generated for a single test session.

    Attributes:
        kid: Key id advertised in JWT headers and in the JWKS document.
        private_pem: PKCS#8 PEM used to sign test tokens.
        public_jwk: Public half, shaped like a Cognito JWKS entry.
    """

    kid: str
    private_pem: str
    public_jwk: dict[str, Any]


class TokenFactory(Protocol):
    """Callable that mints a signed JWT for tests."""

    def __call__(
        self,
        *,
        overrides: Mapping[str, Any] | None = None,
        remove: Iterable[str] = (),
        key_pair: RsaKeyPair | None = None,
        lifetime_seconds: int = 3600,
    ) -> str:
        """Mint a token.

        Args:
            overrides: Claims to replace or add.
            remove: Claims to drop from the default set.
            key_pair: Key to sign with. Defaults to the pair published in JWKS.
            lifetime_seconds: Offset applied to ``exp``. Negative values expire
                the token.

        Returns:
            The encoded JWT.
        """
        ...  # pragma: no cover - protocol definition


def _b64u_uint(value: int) -> str:
    """Encode a positive integer as an unpadded base64url string (RFC 7518)."""
    raw = value.to_bytes((value.bit_length() + 7) // 8, "big")
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")


def generate_key_pair(kid: str) -> RsaKeyPair:
    """Generate a fresh RSA key pair and its JWKS representation.

    Args:
        kid: Key id to embed in the JWK.

    Returns:
        The generated key pair.
    """
    private_key = rsa.generate_private_key(public_exponent=RSA_PUBLIC_EXPONENT, key_size=RSA_KEY_SIZE)
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode("ascii")
    numbers = private_key.public_key().public_numbers()
    public_jwk = {
        "kty": "RSA",
        "alg": "RS256",
        "use": "sig",
        "kid": kid,
        "n": _b64u_uint(numbers.n),
        "e": _b64u_uint(numbers.e),
    }
    return RsaKeyPair(kid=kid, private_pem=private_pem, public_jwk=public_jwk)


@pytest.fixture(scope="session")
def signing_key_pair() -> RsaKeyPair:
    """Return the key pair whose public half is published in the JWKS document."""
    return generate_key_pair(TEST_SIGNING_KID)


@pytest.fixture(scope="session")
def rogue_key_pair() -> RsaKeyPair:
    """Return a key pair using the same ``kid`` but a different, unpublished key.

    Signing with this pair produces a token that resolves a JWKS key but fails
    signature verification.
    """
    return generate_key_pair(TEST_SIGNING_KID)


@pytest.fixture(scope="session")
def auth_settings() -> AuthSettings:
    """Return Cognito settings pointing at a fictional user pool."""
    return AuthSettings(
        user_pool_id=TEST_USER_POOL_ID,
        region=TEST_REGION,
        app_client_id=TEST_APP_CLIENT_ID,
    )


@pytest.fixture
def jwks_document(signing_key_pair: RsaKeyPair) -> dict[str, Any]:
    """Return a JWKS document containing the published signing key."""
    return {"keys": [dict(signing_key_pair.public_jwk)]}


@pytest.fixture
async def jwks_client(auth_settings: AuthSettings, jwks_document: dict[str, Any]) -> AsyncIterator[JwksClient]:
    """Yield a JWKS client backed by an in-memory transport."""

    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=jwks_document)

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http_client:
        yield JwksClient(auth_settings.jwks_url, http_client=http_client)


@pytest.fixture
def mint_token(auth_settings: AuthSettings, signing_key_pair: RsaKeyPair) -> TokenFactory:
    """Return a factory that mints Cognito-shaped ID tokens."""

    def _mint(
        *,
        overrides: Mapping[str, Any] | None = None,
        remove: Iterable[str] = (),
        key_pair: RsaKeyPair | None = None,
        lifetime_seconds: int = 3600,
    ) -> str:
        issued_at = int(time.time())
        claims: dict[str, Any] = {
            "sub": TEST_SUB,
            "email": TEST_EMAIL,
            "email_verified": True,
            "custom:tenant_id": TEST_TENANT_ID,
            "custom:role": TEST_ROLE,
            "token_use": "id",
            "aud": auth_settings.app_client_id,
            "iss": auth_settings.issuer,
            "iat": issued_at,
            "auth_time": issued_at,
            "exp": issued_at + lifetime_seconds,
            # Present on real Cognito ID tokens; only checkable alongside the
            # access token, so validation must skip it.
            "at_hash": "Zm9yLXRlc3RzLW9ubHk",
        }
        claims.update(overrides or {})
        for claim in remove:
            claims.pop(claim, None)

        pair = key_pair or signing_key_pair
        return jwt.encode(claims, pair.private_pem, algorithm="RS256", headers={"kid": pair.kid})

    return _mint
