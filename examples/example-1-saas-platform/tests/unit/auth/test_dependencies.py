"""Unit tests for the FastAPI dependency and the RFC 7807 error responses.

``validate_token`` is replaced with a stub so these tests cover only the HTTP
surface: status codes, headers, and response bodies.
"""

from collections.abc import Iterator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from auth import dependencies
from auth.dependencies import CurrentUserDep, register_exception_handlers
from auth.exceptions import (
    PROBLEM_JSON_MEDIA_TYPE,
    AuthorizationError,
    ExpiredToken,
    InvalidClaims,
    InvalidSignature,
    MissingCredentials,
)
from auth.models import CurrentUser

PROTECTED_PATH = "/api/v1/whoami"
FORBIDDEN_PATH = "/api/v1/tenant-settings"

TEST_USER = CurrentUser(
    sub="11111111-2222-3333-4444-555555555555",
    email="dana@tenant-abc.example.com",
    tenant_id="tenant-abc",
    role="member",
)


@pytest.fixture
def app() -> FastAPI:
    """Return a minimal application with one protected and one forbidden route."""
    application = FastAPI()
    register_exception_handlers(application)

    @application.get(PROTECTED_PATH)
    async def whoami(current_user: CurrentUserDep) -> dict[str, str]:
        """Return the caller's tenant and role."""
        return {"tenant_id": current_user.tenant_id, "role": current_user.role}

    @application.get(FORBIDDEN_PATH)
    async def tenant_settings(current_user: CurrentUserDep) -> dict[str, str]:
        """Stand in for a route that authenticates but denies the caller."""
        raise AuthorizationError(f"Role '{current_user.role}' may not manage tenant settings.")

    return application


@pytest.fixture
def client(app: FastAPI) -> Iterator[TestClient]:
    """Yield a test client that does not raise server exceptions itself."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def accepted_tokens(monkeypatch: pytest.MonkeyPatch) -> list[str]:
    """Stub ``validate_token`` to accept every token, recording what it received."""
    recorded: list[str] = []

    async def fake_validate_token(token: str) -> CurrentUser:
        """Record the token and return a fixed caller."""
        recorded.append(token)
        return TEST_USER

    monkeypatch.setattr(dependencies, "validate_token", fake_validate_token)
    return recorded


def reject_with(monkeypatch: pytest.MonkeyPatch, error: Exception) -> None:
    """Stub ``validate_token`` so it always raises ``error``."""

    async def fake_validate_token(_token: str) -> CurrentUser:
        """Always fail validation."""
        raise error

    monkeypatch.setattr(dependencies, "validate_token", fake_validate_token)


def test_valid_token_reaches_the_route(client: TestClient, accepted_tokens: list[str]) -> None:
    """Acceptance criterion 1: a valid token lets the request proceed."""
    response = client.get(PROTECTED_PATH, headers={"Authorization": "Bearer valid.jwt.token"})

    assert response.status_code == 200
    assert response.json() == {"tenant_id": "tenant-abc", "role": "member"}
    assert accepted_tokens == ["valid.jwt.token"]


def test_missing_authorization_header_returns_401_challenge(client: TestClient) -> None:
    """Acceptance criterion 6: no header means 401 plus a Bearer challenge."""
    response = client.get(PROTECTED_PATH)

    assert response.status_code == 401
    assert response.headers["WWW-Authenticate"] == "Bearer"
    assert response.headers["content-type"].startswith(PROBLEM_JSON_MEDIA_TYPE)

    problem = response.json()
    assert problem["status"] == 401
    assert problem["title"] == "Missing Credentials"
    assert problem["type"].endswith("/missing-credentials")
    assert problem["instance"] == PROTECTED_PATH
    assert "Bearer" in problem["detail"]


@pytest.mark.parametrize(
    "header",
    [
        pytest.param("Basic dXNlcjpwYXNz", id="wrong-scheme"),
        pytest.param("Bearer", id="scheme-without-token"),
        pytest.param("", id="empty-header"),
    ],
)
def test_unusable_authorization_header_returns_401(client: TestClient, header: str) -> None:
    """Anything that is not a Bearer token is treated as missing credentials."""
    response = client.get(PROTECTED_PATH, headers={"Authorization": header})

    assert response.status_code == 401
    assert response.headers["WWW-Authenticate"] == "Bearer"


@pytest.mark.parametrize(
    ("error", "expected_type_suffix"),
    [
        pytest.param(ExpiredToken("Token has expired."), "/expired-token", id="expired"),
        pytest.param(InvalidSignature("Bad signature."), "/invalid-signature", id="bad-signature"),
        pytest.param(InvalidClaims("Wrong audience."), "/invalid-claims", id="bad-claims"),
        pytest.param(MissingCredentials("No token."), "/missing-credentials", id="missing"),
    ],
)
def test_authentication_failures_return_problem_details(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
    error: Exception,
    expected_type_suffix: str,
) -> None:
    """Acceptance criteria 2 and 3: each failure mode maps to a 401 problem."""
    reject_with(monkeypatch, error)

    response = client.get(PROTECTED_PATH, headers={"Authorization": "Bearer some.jwt.token"})

    assert response.status_code == 401
    assert response.headers["WWW-Authenticate"] == "Bearer"
    assert response.headers["content-type"].startswith(PROBLEM_JSON_MEDIA_TYPE)

    problem = response.json()
    assert problem["type"].endswith(expected_type_suffix)
    assert problem["status"] == 401
    assert problem["instance"] == PROTECTED_PATH
    assert set(problem) == {"type", "title", "status", "detail", "instance"}


def test_authorization_failure_returns_403_without_challenge(client: TestClient, accepted_tokens: list[str]) -> None:
    """An authenticated but unpermitted caller gets 403 and no auth challenge."""
    response = client.get(FORBIDDEN_PATH, headers={"Authorization": "Bearer valid.jwt.token"})

    assert response.status_code == 403
    assert "WWW-Authenticate" not in response.headers
    assert accepted_tokens == ["valid.jwt.token"]

    problem = response.json()
    assert problem["status"] == 403
    assert problem["title"] == "Forbidden"
    assert problem["type"].endswith("/forbidden")
    assert problem["instance"] == FORBIDDEN_PATH


def test_problem_body_never_echoes_the_token(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    """Error payloads must not leak credentials back to the caller or logs."""
    reject_with(monkeypatch, InvalidSignature("Token signature could not be verified."))

    response = client.get(PROTECTED_PATH, headers={"Authorization": "Bearer super.secret.token"})

    assert "super.secret.token" not in response.text
