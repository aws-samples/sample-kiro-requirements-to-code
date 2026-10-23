"""FastAPI wiring for authentication.

Route handlers depend on :func:`get_current_user` (or the ``CurrentUserDep``
alias) to receive a validated :class:`~auth.models.CurrentUser`. Applications
call :func:`register_exception_handlers` once at startup so auth failures are
rendered as RFC 7807 Problem Details instead of FastAPI's default payload.
"""

import logging
from typing import Annotated, Final

from fastapi import Depends, FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from auth.exceptions import (
    PROBLEM_JSON_MEDIA_TYPE,
    AppException,
    AuthenticationError,
    AuthorizationError,
    MissingCredentials,
)
from auth.models import CurrentUser
from auth.token import validate_token

logger = logging.getLogger(__name__)

WWW_AUTHENTICATE_HEADER: Final[str] = "WWW-Authenticate"
"""Header RFC 7235 requires on 401 responses."""

BEARER_CHALLENGE: Final[str] = "Bearer"
"""Challenge advertised to unauthenticated callers."""

bearer_scheme = HTTPBearer(
    auto_error=False,
    scheme_name="CognitoIdToken",
    description="Cognito ID token for the signed-in user.",
)
"""Extracts the Bearer token. ``auto_error=False`` so this package owns the
error shape: FastAPI's built-in error is neither Problem Details nor guaranteed
to carry a ``WWW-Authenticate`` header."""


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
) -> CurrentUser:
    """Validate the request's Bearer token and return the caller.

    Args:
        credentials: Parsed ``Authorization`` header, or ``None`` when the header
            is absent, empty, or does not use the Bearer scheme.

    Returns:
        The authenticated caller.

    Raises:
        MissingCredentials: If no Bearer token was supplied.
        AuthenticationError: Any subclass raised by
            :func:`~auth.token.validate_token` for an unusable token.
    """
    if credentials is None:
        raise MissingCredentials("An 'Authorization: Bearer <token>' header is required.")
    return await validate_token(credentials.credentials)


CurrentUserDep = Annotated[CurrentUser, Depends(get_current_user)]
"""Convenience alias: ``def route(user: CurrentUserDep) -> ...``."""


def build_problem_response(
    request: Request,
    exc: AppException,
    *,
    headers: dict[str, str] | None = None,
) -> JSONResponse:
    """Render an application exception as an RFC 7807 response.

    Args:
        request: Request being handled, used for the ``instance`` member.
        exc: Exception carrying the status code and problem metadata.
        headers: Extra response headers.

    Returns:
        A ``application/problem+json`` response.
    """
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.to_problem_detail(instance=request.url.path),
        media_type=PROBLEM_JSON_MEDIA_TYPE,
        headers=headers,
    )


async def auth_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Map authentication and authorization failures to 401/403 responses.

    Authentication failures get ``WWW-Authenticate: Bearer`` so clients know how
    to retry. Details are logged at INFO: failed auth is an expected condition,
    not a server fault, and the messages never include token contents.

    Args:
        request: Request being handled.
        exc: The raised exception. Typed as :class:`Exception` to match
            Starlette's handler signature.

    Returns:
        A Problem Details response.

    Raises:
        Exception: Re-raises anything that is not an auth exception, so an
            accidental registration cannot silently swallow unrelated errors.
    """
    if isinstance(exc, AuthenticationError):
        logger.info("Authentication failed on %s %s: %s", request.method, request.url.path, exc.detail)
        return build_problem_response(request, exc, headers={WWW_AUTHENTICATE_HEADER: BEARER_CHALLENGE})

    if isinstance(exc, AuthorizationError):
        logger.info("Authorization denied on %s %s: %s", request.method, request.url.path, exc.detail)
        return build_problem_response(request, exc)

    raise exc


def register_exception_handlers(app: FastAPI) -> None:
    """Register the auth exception handlers on an application.

    Args:
        app: The FastAPI application to configure.
    """
    app.add_exception_handler(AuthenticationError, auth_exception_handler)
    app.add_exception_handler(AuthorizationError, auth_exception_handler)
