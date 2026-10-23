"""RFC 7807 Problem Details helpers for API Gateway proxy responses.

The helpers here are deliberately dependency-free (standard library only) so
that they can be imported by any function in the pipeline without pulling the
shared Pydantic models into the import graph.
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from http import HTTPStatus
from typing import Any, Final

JSON_CONTENT_TYPE: Final[str] = "application/json"
PROBLEM_CONTENT_TYPE: Final[str] = "application/problem+json"
PROBLEM_TYPE_BASE: Final[str] = "https://streamprocess.example.com/problems"
CORRELATION_ID_HEADER: Final[str] = "x-correlation-id"


def default_problem_type(status: int) -> str:
    """Derive a stable problem type URI from an HTTP status code.

    Args:
        status: HTTP status code, e.g. ``415``.

    Returns:
        A URI such as ``https://streamprocess.example.com/problems/unsupported-media-type``.
    """
    try:
        slug = HTTPStatus(status).phrase.lower().replace(" ", "-")
    except ValueError:
        slug = f"http-{status}"
    return f"{PROBLEM_TYPE_BASE}/{slug}"


def problem_detail(
    *,
    status: int,
    title: str,
    detail: str,
    problem_type: str | None = None,
    instance: str | None = None,
    extensions: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build an RFC 7807 Problem Details document.

    Args:
        status: HTTP status code for the response.
        title: Short, human-readable summary of the problem type.
        detail: Human-readable explanation specific to this occurrence.
        problem_type: Problem type URI. Derived from ``status`` when omitted.
        instance: URI reference identifying this specific occurrence.
        extensions: Additional members merged into the document, such as
            ``correlation_id``. Reserved members are never overwritten.

    Returns:
        The Problem Details document as a JSON-serialisable dictionary.
    """
    document: dict[str, Any] = {
        "type": problem_type if problem_type is not None else default_problem_type(status),
        "title": title,
        "status": status,
        "detail": detail,
    }
    if instance is not None:
        document["instance"] = instance
    if extensions:
        document.update({key: value for key, value in extensions.items() if key not in document})
    return document


def json_response(
    *,
    status: int,
    body: Mapping[str, Any],
    correlation_id: str | None = None,
    content_type: str = JSON_CONTENT_TYPE,
) -> dict[str, Any]:
    """Wrap a JSON body in an API Gateway proxy integration response.

    Args:
        status: HTTP status code for the response.
        body: JSON-serialisable response body.
        correlation_id: Correlation ID echoed back in a response header.
        content_type: Value for the ``Content-Type`` response header.

    Returns:
        A proxy integration response dictionary with a serialised body.
    """
    headers = {"Content-Type": content_type}
    if correlation_id is not None:
        headers[CORRELATION_ID_HEADER] = correlation_id
    return {
        "statusCode": int(status),
        "headers": headers,
        "body": json.dumps(body, separators=(",", ":")),
        "isBase64Encoded": False,
    }


def problem_response(
    *,
    status: int,
    title: str,
    detail: str,
    problem_type: str | None = None,
    instance: str | None = None,
    correlation_id: str | None = None,
    extensions: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build an API Gateway proxy response carrying a Problem Details body.

    Args:
        status: HTTP status code for the response.
        title: Short, human-readable summary of the problem type.
        detail: Human-readable explanation specific to this occurrence.
        problem_type: Problem type URI. Derived from ``status`` when omitted.
        instance: URI reference identifying this specific occurrence.
        correlation_id: Correlation ID added to the document and the headers.
        extensions: Additional members merged into the document.

    Returns:
        A proxy integration response whose body is a Problem Details document
        served as ``application/problem+json``.
    """
    members: dict[str, Any] = dict(extensions or {})
    if correlation_id is not None:
        members.setdefault("correlation_id", correlation_id)
    document = problem_detail(
        status=status,
        title=title,
        detail=detail,
        problem_type=problem_type,
        instance=instance,
        extensions=members,
    )
    return json_response(
        status=status,
        body=document,
        correlation_id=correlation_id,
        content_type=PROBLEM_CONTENT_TYPE,
    )
