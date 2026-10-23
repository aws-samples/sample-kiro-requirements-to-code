"""Domain exceptions for authentication and authorization.

Every exception inherits from :class:`AppException` and carries the HTTP status
code plus the RFC 7807 Problem Details metadata it maps to. Routes and
middleware translate these to responses; business logic never imports HTTP
types (see ``.kiro/steering/coding-standards.md``).
"""

from typing import Any, ClassVar

PROBLEM_JSON_MEDIA_TYPE = "application/problem+json"
"""Media type mandated by RFC 7807 for Problem Details payloads."""

_PROBLEM_TYPE_BASE = "https://taskflow.example.com/problems"


class AppException(Exception):
    """Base class for all TaskFlow application exceptions.

    Attributes:
        status_code: HTTP status the exception maps to.
        title: Short, human-readable summary used as the Problem Details title.
        problem_type: URI identifying the problem type.
    """

    status_code: ClassVar[int] = 500
    title: ClassVar[str] = "Internal Server Error"
    problem_type: ClassVar[str] = f"{_PROBLEM_TYPE_BASE}/internal-error"

    def __init__(self, detail: str) -> None:
        """Initialise the exception.

        Args:
            detail: Human-readable explanation specific to this occurrence. Must
                never contain token contents, secrets, or other credentials.
        """
        super().__init__(detail)
        self.detail = detail

    def to_problem_detail(self, instance: str | None = None) -> dict[str, Any]:
        """Render the exception as an RFC 7807 Problem Details document.

        Args:
            instance: Optional URI reference identifying the specific occurrence,
                normally the request path.

        Returns:
            A JSON-serialisable Problem Details mapping.
        """
        problem: dict[str, Any] = {
            "type": self.problem_type,
            "title": self.title,
            "status": self.status_code,
            "detail": self.detail,
        }
        if instance is not None:
            problem["instance"] = instance
        return problem


class AuthenticationError(AppException):
    """The caller could not be authenticated. Maps to HTTP 401."""

    status_code: ClassVar[int] = 401
    title: ClassVar[str] = "Unauthorized"
    problem_type: ClassVar[str] = f"{_PROBLEM_TYPE_BASE}/unauthorized"


class AuthorizationError(AppException):
    """The caller is authenticated but not permitted. Maps to HTTP 403."""

    status_code: ClassVar[int] = 403
    title: ClassVar[str] = "Forbidden"
    problem_type: ClassVar[str] = f"{_PROBLEM_TYPE_BASE}/forbidden"


class MissingCredentials(AuthenticationError):
    """No usable ``Authorization: Bearer <token>`` header was supplied."""

    title: ClassVar[str] = "Missing Credentials"
    problem_type: ClassVar[str] = f"{_PROBLEM_TYPE_BASE}/missing-credentials"


class ExpiredToken(AuthenticationError):
    """The token signature is valid but the ``exp`` claim has passed."""

    title: ClassVar[str] = "Expired Token"
    problem_type: ClassVar[str] = f"{_PROBLEM_TYPE_BASE}/expired-token"


class InvalidSignature(AuthenticationError):
    """The token signature could not be verified against the user pool JWKS."""

    title: ClassVar[str] = "Invalid Token Signature"
    problem_type: ClassVar[str] = f"{_PROBLEM_TYPE_BASE}/invalid-signature"


class InvalidClaims(AuthenticationError):
    """A required claim is missing or holds an unexpected value."""

    title: ClassVar[str] = "Invalid Token Claims"
    problem_type: ClassVar[str] = f"{_PROBLEM_TYPE_BASE}/invalid-claims"


class SigningKeyUnavailable(AuthenticationError):
    """No signing key is available for the token's ``kid``.

    Raised when the JWKS document has never been fetched successfully and no
    cached copy exists, or when the ``kid`` is absent from the fetched document.
    """

    title: ClassVar[str] = "Signing Key Unavailable"
    problem_type: ClassVar[str] = f"{_PROBLEM_TYPE_BASE}/signing-key-unavailable"
