"""Unit tests for the JWKS client: caching, TTL, and outage tolerance.

HTTP is served by :class:`httpx.MockTransport` and time comes from an injected
clock, so the tests are network-free and deterministic.
"""

import asyncio
import logging
from collections.abc import AsyncIterator
from typing import Any

import httpx
import pytest

from auth.config import AuthSettings
from auth.exceptions import SigningKeyUnavailable
from auth.jwks import JWKS_CACHE_TTL_SECONDS, JwksClient

from .conftest import TEST_SIGNING_KID


class FakeClock:
    """A manually advanced monotonic clock."""

    def __init__(self, now: float = 1_000.0) -> None:
        """Start the clock at ``now`` seconds."""
        self._now = now

    def __call__(self) -> float:
        """Return the current fake time in seconds."""
        return self._now

    def advance(self, seconds: float) -> None:
        """Move the clock forward."""
        self._now += seconds


class JwksEndpoint:
    """A scripted JWKS endpoint that records how often it is called."""

    def __init__(self, document: dict[str, Any]) -> None:
        """Serve ``document`` until reconfigured by a test."""
        self.document = document
        self.calls = 0
        self.failure: Exception | None = None
        self.status_code = 200

    def handler(self, request: httpx.Request) -> httpx.Response:
        """Serve the configured response, or raise the configured failure."""
        self.calls += 1
        if self.failure is not None:
            raise self.failure
        return httpx.Response(self.status_code, json=self.document, request=request)


def build_client(settings: AuthSettings, clock: FakeClock, http_client: httpx.AsyncClient) -> JwksClient:
    """Wire a :class:`JwksClient` to a scripted endpoint's transport."""
    return JwksClient(settings.jwks_url, http_client=http_client, clock=clock)


@pytest.fixture
def endpoint(jwks_document: dict[str, Any]) -> JwksEndpoint:
    """Return a scripted JWKS endpoint serving the test document."""
    return JwksEndpoint(jwks_document)


@pytest.fixture
def clock() -> FakeClock:
    """Return a manually advanced clock."""
    return FakeClock()


@pytest.fixture
async def client(
    endpoint: JwksEndpoint,
    auth_settings: AuthSettings,
    clock: FakeClock,
) -> AsyncIterator[JwksClient]:
    """Yield a JWKS client wired to the scripted endpoint."""
    async with httpx.AsyncClient(transport=httpx.MockTransport(endpoint.handler)) as http_client:
        yield build_client(auth_settings, clock, http_client)


async def test_get_signing_key_returns_key_matching_kid(client: JwksClient, endpoint: JwksEndpoint) -> None:
    """Task 2.2: the key is looked up by the ``kid`` from the JWT header."""
    key = await client.get_signing_key(TEST_SIGNING_KID)

    assert key["kid"] == TEST_SIGNING_KID
    assert key["kty"] == "RSA"
    assert endpoint.calls == 1


async def test_unknown_kid_raises(client: JwksClient) -> None:
    """A key id absent from the document is reported, not silently ignored."""
    with pytest.raises(SigningKeyUnavailable, match="rotated-key"):
        await client.get_signing_key("rotated-key")


async def test_repeated_lookups_within_ttl_hit_the_cache(client: JwksClient, endpoint: JwksEndpoint) -> None:
    """The document is fetched once while the cache is fresh."""
    await client.get_signing_key(TEST_SIGNING_KID)
    await client.get_signing_key(TEST_SIGNING_KID)
    await client.get_signing_key(TEST_SIGNING_KID)

    assert endpoint.calls == 1


async def test_cache_is_reused_up_to_the_ttl_boundary(
    client: JwksClient, endpoint: JwksEndpoint, clock: FakeClock
) -> None:
    """One second before the TTL elapses the cached copy is still served."""
    await client.get_signing_key(TEST_SIGNING_KID)
    clock.advance(JWKS_CACHE_TTL_SECONDS - 1)

    await client.get_signing_key(TEST_SIGNING_KID)

    assert endpoint.calls == 1


async def test_cache_refreshes_after_ttl_expires(client: JwksClient, endpoint: JwksEndpoint, clock: FakeClock) -> None:
    """Once the 1 hour TTL elapses the document is fetched again."""
    await client.get_signing_key(TEST_SIGNING_KID)
    clock.advance(JWKS_CACHE_TTL_SECONDS + 1)

    await client.get_signing_key(TEST_SIGNING_KID)

    assert endpoint.calls == 2


async def test_concurrent_lookups_trigger_a_single_fetch(client: JwksClient, endpoint: JwksEndpoint) -> None:
    """A burst of cold-cache requests is collapsed into one fetch."""
    results = await asyncio.gather(*(client.get_signing_key(TEST_SIGNING_KID) for _ in range(5)))

    assert endpoint.calls == 1
    assert all(key["kid"] == TEST_SIGNING_KID for key in results)


async def test_stale_cache_is_served_when_refresh_fails(
    client: JwksClient,
    endpoint: JwksEndpoint,
    clock: FakeClock,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Acceptance criterion 5: a JWKS outage falls back to the cached keys."""
    await client.get_signing_key(TEST_SIGNING_KID)
    clock.advance(JWKS_CACHE_TTL_SECONDS + 1)
    endpoint.failure = httpx.ConnectError("cognito unreachable")

    with caplog.at_level(logging.WARNING, logger="auth.jwks"):
        key = await client.get_signing_key(TEST_SIGNING_KID)

    assert key["kid"] == TEST_SIGNING_KID
    assert endpoint.calls == 2
    assert "serving cached keys" in caplog.text


async def test_http_error_status_falls_back_to_cache(
    client: JwksClient, endpoint: JwksEndpoint, clock: FakeClock
) -> None:
    """A 5xx from the JWKS endpoint is treated the same as a transport error."""
    await client.get_signing_key(TEST_SIGNING_KID)
    clock.advance(JWKS_CACHE_TTL_SECONDS + 1)
    endpoint.status_code = 503

    key = await client.get_signing_key(TEST_SIGNING_KID)

    assert key["kid"] == TEST_SIGNING_KID


async def test_fetch_failure_without_cache_raises(client: JwksClient, endpoint: JwksEndpoint) -> None:
    """With nothing cached there is nothing to fall back to."""
    endpoint.failure = httpx.ConnectError("cognito unreachable")

    with pytest.raises(SigningKeyUnavailable, match="could not be fetched"):
        await client.get_signing_key(TEST_SIGNING_KID)


@pytest.mark.parametrize(
    "document",
    [
        pytest.param({}, id="no-keys-member"),
        pytest.param({"keys": []}, id="empty-keys"),
        pytest.param({"keys": [{"kty": "RSA"}]}, id="key-without-kid"),
        pytest.param({"keys": "not-a-list"}, id="keys-not-a-list"),
    ],
)
async def test_malformed_document_raises(
    endpoint: JwksEndpoint,
    auth_settings: AuthSettings,
    clock: FakeClock,
    document: dict[str, Any],
) -> None:
    """A payload that is not a usable JWKS document is rejected."""
    endpoint.document = document

    async with httpx.AsyncClient(transport=httpx.MockTransport(endpoint.handler)) as http_client:
        client = build_client(auth_settings, clock, http_client)

        with pytest.raises(SigningKeyUnavailable):
            await client.get_signing_key(TEST_SIGNING_KID)


async def test_jwks_url_is_derived_from_settings(client: JwksClient, auth_settings: AuthSettings) -> None:
    """The client fetches the user pool's well-known JWKS path."""
    assert client.jwks_url == auth_settings.jwks_url
    assert client.jwks_url.endswith("/.well-known/jwks.json")
