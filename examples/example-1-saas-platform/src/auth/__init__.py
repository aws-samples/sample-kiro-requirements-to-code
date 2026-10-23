"""Authentication package: Cognito JWT validation for the TaskFlow API.

Public surface:
    * :class:`auth.models.CurrentUser` — typed view of the validated token claims.
    * :func:`auth.dependencies.get_current_user` — FastAPI dependency for protected routes.
    * :func:`auth.dependencies.register_exception_handlers` — RFC 7807 error responses.
    * :func:`auth.token.validate_token` — signature and claim verification.
"""

from auth.dependencies import get_current_user, register_exception_handlers
from auth.exceptions import (
    AppException,
    AuthenticationError,
    AuthorizationError,
    ExpiredToken,
    InvalidClaims,
    InvalidSignature,
    MissingCredentials,
    SigningKeyUnavailable,
)
from auth.models import CurrentUser
from auth.token import validate_token

__all__ = [
    "AppException",
    "AuthenticationError",
    "AuthorizationError",
    "CurrentUser",
    "ExpiredToken",
    "InvalidClaims",
    "InvalidSignature",
    "MissingCredentials",
    "SigningKeyUnavailable",
    "get_current_user",
    "register_exception_handlers",
    "validate_token",
]
