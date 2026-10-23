"""JWKS retrieval and caching for the Cognito user pool.

Cognito publishes its public signing keys at
``https://cognito-idp.<region>.amazonaws.com/<user_pool_id>/.well-known/jwks.json``.
Fetching that document on every request would add latency and a hard runtime
dependency on Cognito availability, so keys are cached in memory for one hour.
If a refresh fails while a cached copy exists the stale copy is reused and a
warning is logged, which keeps token validation working through short Cognito
or network outages (acceptance criterion 5 of story A2).
"""

import asyncio
import logging
import time
from collections.abc import Callable
from dataclasses import dataclass
from functools import lru_cache
from typing import Any, Final

import httpx

from auth.config import get_auth_settings
from auth.exceptions import SigningKeyUnavailable

logger = logging.getLogger(__name__)

JWKS_CACHE_TTL_SECONDS: Final[int] = 3600
"""How long a fetched JWKS document is served without re-fetching (1 hour)."""

JWKS_HTTP_TIMEOUT_SECONDS: Final[float] = 5.0
"""Timeout applied to the JWKS HTTP request."""

JsonWebKey = dict[str, Any]
"""A single JWK entry as published by Cognito, keyed by JWK parameter name."""


@dataclass(frozen=True)
class _CachedKeys:
    """A snapshot of the JWKS document keyed by ``kid``."""

    keys: dict[str, JsonWebKey]
    fetched_at: float


class JwksClient:
    """Fetches the user pool JWKS document and caches it with a TTL.

    The client is safe to share across concurrent requests: refreshes are
    serialised with an :class:`asyncio.Lock` so a burst of requests triggers a
    single fetch.
    """

    def __init__(
        self,
        jwks_url: str,
        *,
        ttl_seconds: int = JWKS_CACHE_TTL_SECONDS,
        http_client: httpx.AsyncClient | None = None,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        """Initialise the client.

        Args:
            jwks_url: Absolute URL of the JWKS document.
            ttl_seconds: Seconds a fetched document stays fresh.
            http_client: Optional client to reuse. When omitted a short-lived
                :class:`httpx.AsyncClient` is created per fetch.
            clock: Monotonic time source, injectable for tests.
        """
        self._jwks_url = jwks_url
        self._ttl_seconds = ttl_seconds
        self._http_client = http_client
        self._clock = clock
        self._cache: _CachedKeys | None = None
        self._lock = asyncio.Lock()

    @property
    def jwks_url(self) -> str:
        """Return the configured JWKS document URL."""
        return self._jwks_url

    async def get_signing_key(self, kid: str) -> JsonWebKey:
        """Return the JWK whose ``kid`` matches the token header.

        Args:
            kid: Key id taken from the unverified JWT header.

        Returns:
            The matching JWK.

        Raises:
            SigningKeyUnavailable: If no keys can be loaded, or the loaded
                document has no entry for ``kid``.
        """
        keys = await self._load_keys()
        key = keys.get(kid)
        if key is None:
            raise SigningKeyUnavailable(f"No signing key matches key id '{kid}'.")
        return key

    async def _load_keys(self) -> dict[str, JsonWebKey]:
        """Return cached keys when fresh, otherwise refresh them.

        Returns:
            Keys indexed by ``kid``.

        Raises:
            SigningKeyUnavailable: If the fetch fails and no cached copy exists.
        """
        async with self._lock:
            cached = self._cache
            if cached is not None and self._is_fresh(cached):
                return cached.keys

            try:
                keys = await self._fetch_keys()
            except (httpx.HTTPError, ValueError) as exc:
                if cached is not None:
                    logger.warning(
                        "JWKS refresh from %s failed (%s: %s); serving cached keys.",
                        self._jwks_url,
                        type(exc).__name__,
                        exc,
                    )
                    return cached.keys
                raise SigningKeyUnavailable(
                    "Signing keys are unavailable: the JWKS document could not be fetched."
                ) from exc

            self._cache = _CachedKeys(keys=keys, fetched_at=self._clock())
            return keys

    def _is_fresh(self, cached: _CachedKeys) -> bool:
        """Return whether ``cached`` is still within the TTL window."""
        return (self._clock() - cached.fetched_at) < self._ttl_seconds

    async def _fetch_keys(self) -> dict[str, JsonWebKey]:
        """Fetch and parse the JWKS document.

        Returns:
            Keys indexed by ``kid``.

        Raises:
            httpx.HTTPError: If the request fails or returns a non-2xx status.
            ValueError: If the payload is not a JWKS document with usable keys.
        """
        if self._http_client is not None:
            response = await self._http_client.get(self._jwks_url, timeout=JWKS_HTTP_TIMEOUT_SECONDS)
        else:
            async with httpx.AsyncClient(timeout=JWKS_HTTP_TIMEOUT_SECONDS) as client:
                response = await client.get(self._jwks_url)
        response.raise_for_status()
        return _parse_jwks_document(response.json())


def _parse_jwks_document(document: object) -> dict[str, JsonWebKey]:
    """Index a JWKS payload by ``kid``.

    Args:
        document: Decoded JSON payload from the JWKS endpoint.

    Returns:
        Keys indexed by ``kid``.

    Raises:
        ValueError: If the payload is malformed or holds no identifiable keys.
    """
    if not isinstance(document, dict):
        raise ValueError("JWKS payload is not a JSON object.")

    entries = document.get("keys")
    if not isinstance(entries, list):
        raise ValueError("JWKS payload has no 'keys' array.")

    keys: dict[str, JsonWebKey] = {}
    for entry in entries:
        if isinstance(entry, dict) and isinstance(entry.get("kid"), str):
            keys[entry["kid"]] = entry

    if not keys:
        raise ValueError("JWKS payload contains no keys with a 'kid'.")
    return keys


@lru_cache(maxsize=1)
def get_jwks_client() -> JwksClient:
    """Return the process-wide JWKS client, built once from settings.

    Returns:
        The shared :class:`JwksClient` for the configured user pool.
    """
    return JwksClient(get_auth_settings().jwks_url)
