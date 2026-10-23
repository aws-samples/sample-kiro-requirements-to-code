"""Ingestion errors and their mapping to RFC 7807 Problem Details responses.

Only client errors are modelled here. Anything unexpected is deliberately left
uncaught so the invocation fails, Lambda retries per its configuration, and the
event ends up on the dead-letter queue instead of being silently swallowed.
"""

from __future__ import annotations

from collections.abc import Mapping
from http import HTTPStatus
from typing import Any

from responses import problem_response


class IngestError(Exception):
    """Base class for ingestion errors that map to a Problem Details response.

    Attributes:
        status: HTTP status code returned to the publisher.
        title: Short, human-readable summary of the problem type.
        detail: Explanation specific to this occurrence.
        extensions: Extra members merged into the Problem Details document.
    """

    status: int = HTTPStatus.INTERNAL_SERVER_ERROR
    title: str = "Internal Server Error"

    def __init__(self, detail: str, *, extensions: Mapping[str, Any] | None = None) -> None:
        """Initialise the error.

        Args:
            detail: Explanation specific to this occurrence.
            extensions: Extra members merged into the Problem Details document.
        """
        super().__init__(detail)
        self.detail = detail
        self.extensions: dict[str, Any] = dict(extensions or {})

    def to_response(self, *, correlation_id: str | None = None, instance: str | None = None) -> dict[str, Any]:
        """Render the error as an API Gateway proxy response.

        Args:
            correlation_id: Correlation ID echoed to the publisher.
            instance: URI reference identifying this specific occurrence.

        Returns:
            A proxy integration response carrying a Problem Details body.
        """
        return problem_response(
            status=self.status,
            title=self.title,
            detail=self.detail,
            instance=instance,
            correlation_id=correlation_id,
            extensions=self.extensions,
        )


class UnsupportedMediaTypeError(IngestError):
    """Raised when the request is not declared as ``application/json``."""

    status: int = HTTPStatus.UNSUPPORTED_MEDIA_TYPE
    title: str = "Unsupported Media Type"


class EmptyBodyError(IngestError):
    """Raised when the request body is missing, empty or whitespace only."""

    status: int = HTTPStatus.BAD_REQUEST
    title: str = "Empty Request Body"


class MalformedEventError(IngestError):
    """Raised when the request body is not a JSON object."""

    status: int = HTTPStatus.BAD_REQUEST
    title: str = "Malformed Event"
