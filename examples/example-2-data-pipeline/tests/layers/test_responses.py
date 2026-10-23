"""Tests for the shared RFC 7807 Problem Details helpers."""

from __future__ import annotations

import json
from http import HTTPStatus

import pytest

from responses import (
    CORRELATION_ID_HEADER,
    JSON_CONTENT_TYPE,
    PROBLEM_CONTENT_TYPE,
    PROBLEM_TYPE_BASE,
    default_problem_type,
    json_response,
    problem_detail,
    problem_response,
)

CORRELATION_ID = "0190a0f4-8f1e-7c3a-9f2b-6d5c4b3a2e10"


def test_problem_detail_contains_the_rfc7807_members() -> None:
    """The document carries type, title, status, detail and instance."""
    document = problem_detail(
        status=HTTPStatus.BAD_REQUEST,
        title="Empty Request Body",
        detail="Request body must contain a JSON object.",
        instance="/v1/events#req-1",
    )

    assert document == {
        "type": f"{PROBLEM_TYPE_BASE}/bad-request",
        "title": "Empty Request Body",
        "status": HTTPStatus.BAD_REQUEST,
        "detail": "Request body must contain a JSON object.",
        "instance": "/v1/events#req-1",
    }


def test_problem_detail_omits_instance_when_not_supplied() -> None:
    """``instance`` is optional in RFC 7807 and is left out when unknown."""
    document = problem_detail(status=500, title="Internal Server Error", detail="Unexpected failure.")

    assert "instance" not in document


@pytest.mark.parametrize(
    ("status", "expected_slug"),
    [
        (HTTPStatus.BAD_REQUEST, "bad-request"),
        (HTTPStatus.FORBIDDEN, "forbidden"),
        (HTTPStatus.UNSUPPORTED_MEDIA_TYPE, "unsupported-media-type"),
        (HTTPStatus.INTERNAL_SERVER_ERROR, "internal-server-error"),
    ],
)
def test_default_problem_type_is_derived_from_the_status_phrase(status: int, expected_slug: str) -> None:
    """Problem type URIs are stable and readable, derived from the status phrase."""
    assert default_problem_type(status) == f"{PROBLEM_TYPE_BASE}/{expected_slug}"


def test_default_problem_type_falls_back_for_unknown_statuses() -> None:
    """A non-standard status still yields a usable type URI."""
    assert default_problem_type(599) == f"{PROBLEM_TYPE_BASE}/http-599"


def test_explicit_problem_type_overrides_the_default() -> None:
    """Callers can point at a documented problem type of their own."""
    document = problem_detail(
        status=400,
        title="Malformed Event",
        detail="Body is not a JSON object.",
        problem_type="https://streamprocess.example.com/problems/malformed-event",
    )

    assert document["type"] == "https://streamprocess.example.com/problems/malformed-event"


def test_extensions_are_merged_without_overwriting_reserved_members() -> None:
    """Extension members are additive and cannot mask the reserved ones."""
    document = problem_detail(
        status=415,
        title="Unsupported Media Type",
        detail="Content-Type must be application/json.",
        extensions={"expected_content_type": JSON_CONTENT_TYPE, "status": 200, "title": "spoofed"},
    )

    assert document["expected_content_type"] == JSON_CONTENT_TYPE
    assert document["status"] == 415
    assert document["title"] == "Unsupported Media Type"


def test_problem_response_is_served_as_problem_json() -> None:
    """Problem responses use the application/problem+json media type."""
    response = problem_response(status=415, title="Unsupported Media Type", detail="Wrong media type.")

    assert response["statusCode"] == 415
    assert response["headers"]["Content-Type"] == PROBLEM_CONTENT_TYPE
    assert response["isBase64Encoded"] is False
    assert json.loads(response["body"])["title"] == "Unsupported Media Type"


def test_problem_response_propagates_the_correlation_id() -> None:
    """The correlation ID appears both in the headers and in the document."""
    response = problem_response(
        status=400,
        title="Empty Request Body",
        detail="Request body must contain a JSON object.",
        correlation_id=CORRELATION_ID,
    )

    assert response["headers"][CORRELATION_ID_HEADER] == CORRELATION_ID
    assert json.loads(response["body"])["correlation_id"] == CORRELATION_ID


def test_json_response_serialises_the_body_compactly() -> None:
    """Successful responses are JSON encoded without padding whitespace."""
    response = json_response(status=HTTPStatus.ACCEPTED, body={"status": "accepted"}, correlation_id=CORRELATION_ID)

    assert response["statusCode"] == HTTPStatus.ACCEPTED
    assert response["headers"]["Content-Type"] == JSON_CONTENT_TYPE
    assert response["body"] == '{"status":"accepted"}'
    assert response["headers"][CORRELATION_ID_HEADER] == CORRELATION_ID


def test_json_response_omits_the_correlation_header_when_unknown() -> None:
    """No correlation ID means no empty header is emitted."""
    response = json_response(status=200, body={"ok": True})

    assert CORRELATION_ID_HEADER not in response["headers"]
