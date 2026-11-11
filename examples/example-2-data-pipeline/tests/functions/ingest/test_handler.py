"""Tests for the ingestion Lambda handler (story E1 acceptance criteria)."""

from __future__ import annotations

import json
from collections.abc import Callable
from datetime import UTC, datetime
from http import HTTPStatus
from typing import Any
from uuid import UUID

import pytest

from ingest import handler as handler_module
from responses import JSON_CONTENT_TYPE, PROBLEM_CONTENT_TYPE

from .conftest import TEST_SOURCE_IP, CapturedOutput, FakeLambdaContext

EventFactory = Callable[..., dict[str, Any]]
OutputReader = Callable[[], CapturedOutput]


def _invoke(event: dict[str, Any], context: FakeLambdaContext) -> dict[str, Any]:
    """Invoke the handler the way the Lambda runtime does.

    Args:
        event: API Gateway REST proxy event.
        context: Fake Lambda context.

    Returns:
        The proxy integration response.
    """
    return handler_module.handler(event, context)  # type: ignore[arg-type]


def _body(response: dict[str, Any]) -> dict[str, Any]:
    """Decode a proxy response body.

    Args:
        response: Proxy integration response.

    Returns:
        The parsed JSON body.
    """
    parsed = json.loads(response["body"])
    assert isinstance(parsed, dict)
    return parsed


def test_valid_event_returns_202_with_correlation_id(
    api_gateway_event: EventFactory,
    lambda_context: FakeLambdaContext,
) -> None:
    """A valid JSON body is acknowledged with 202 and a correlation ID."""
    response = _invoke(api_gateway_event(), lambda_context)

    assert response["statusCode"] == HTTPStatus.ACCEPTED
    assert response["headers"]["Content-Type"] == JSON_CONTENT_TYPE
    body = _body(response)
    assert body["status"] == "accepted"
    assert body["correlation_id"]
    assert response["headers"]["x-correlation-id"] == body["correlation_id"]


def test_correlation_id_is_a_uuid_v7(
    api_gateway_event: EventFactory,
    lambda_context: FakeLambdaContext,
) -> None:
    """Correlation IDs are time-ordered UUIDv7 values, per the tech guidelines."""
    response = _invoke(api_gateway_event(), lambda_context)

    correlation_id = UUID(_body(response)["correlation_id"])
    assert correlation_id.version == 7


def test_accepted_event_is_logged_with_required_context(
    api_gateway_event: EventFactory,
    lambda_context: FakeLambdaContext,
    captured_output: OutputReader,
) -> None:
    """The structured log entry carries correlation_id, source_ip, timestamp and size."""
    body = '{"event_type": "order.created"}'
    response = _invoke(api_gateway_event(body=body), lambda_context)

    record = captured_output().log_with_message("Event accepted")
    assert record["correlation_id"] == _body(response)["correlation_id"]
    assert record["source_ip"] == TEST_SOURCE_IP
    assert record["event_size_bytes"] == len(body.encode("utf-8"))
    assert record["payload_fields"] == 1
    assert record["level"] == "INFO"
    # The formatter stamps every record in ISO 8601 UTC; received_at is the same
    # instant carried in the metadata that downstream stages reuse.
    assert record["timestamp"].endswith("Z")
    assert datetime.fromisoformat(record["timestamp"]).tzinfo == UTC
    assert record["received_at"].endswith("Z")


def test_accepted_event_emits_business_metrics(
    api_gateway_event: EventFactory,
    lambda_context: FakeLambdaContext,
    captured_output: OutputReader,
) -> None:
    """Ingestion volume is reported through Metrics, not log lines."""
    _invoke(api_gateway_event(), lambda_context)

    published = captured_output().metric_names()
    assert {handler_module.METRIC_EVENTS_RECEIVED, handler_module.METRIC_EVENTS_INGESTED} <= published


def test_handler_does_not_enforce_authentication(
    api_gateway_event: EventFactory,
    lambda_context: FakeLambdaContext,
) -> None:
    """The handler holds no auth logic; it trusts that API Gateway already enforced it.

    This test does NOT verify that unauthenticated requests are rejected. That
    enforcement lives in Terraform: the `/events` method uses
    `authorization = "AWS_IAM"` (SigV4) and `api_key_required = true`, so an
    unsigned request or one without `x-api-key` gets 403 before the function is
    invoked. What this test pins down is the handler's contract: an event that
    reaches it is processed normally regardless of the key header, and the key
    is never echoed back in the response.
    """
    response = _invoke(api_gateway_event(api_key=None), lambda_context)

    assert response["statusCode"] == HTTPStatus.ACCEPTED
    assert "x-api-key" not in json.dumps(_body(response))


@pytest.mark.parametrize("content_type", ["text/plain", "application/xml", "application/json-patch+json", None])
def test_non_json_content_type_returns_415(
    api_gateway_event: EventFactory,
    lambda_context: FakeLambdaContext,
    content_type: str | None,
) -> None:
    """Anything other than application/json is rejected with 415 Problem Details."""
    response = _invoke(api_gateway_event(content_type=content_type), lambda_context)

    assert response["statusCode"] == HTTPStatus.UNSUPPORTED_MEDIA_TYPE
    assert response["headers"]["Content-Type"] == PROBLEM_CONTENT_TYPE
    problem = _body(response)
    assert problem["status"] == HTTPStatus.UNSUPPORTED_MEDIA_TYPE
    assert problem["title"] == "Unsupported Media Type"
    assert problem["type"].endswith("/unsupported-media-type")
    assert problem["expected_content_type"] == JSON_CONTENT_TYPE
    assert problem["correlation_id"]
    assert problem["instance"].startswith("/v1/events")


def test_content_type_with_charset_is_accepted(
    api_gateway_event: EventFactory,
    lambda_context: FakeLambdaContext,
) -> None:
    """Media type parameters such as charset do not change the media type."""
    response = _invoke(api_gateway_event(content_type="application/json; charset=utf-8"), lambda_context)

    assert response["statusCode"] == HTTPStatus.ACCEPTED


@pytest.mark.parametrize("body", [None, "", "   \n  "])
def test_empty_body_returns_400_problem_details(
    api_gateway_event: EventFactory,
    lambda_context: FakeLambdaContext,
    body: str | None,
) -> None:
    """A missing or blank body is rejected with 400 and an explanation."""
    response = _invoke(api_gateway_event(body=body), lambda_context)

    assert response["statusCode"] == HTTPStatus.BAD_REQUEST
    assert response["headers"]["Content-Type"] == PROBLEM_CONTENT_TYPE
    problem = _body(response)
    assert problem["title"] == "Empty Request Body"
    assert problem["detail"] == "Request body must contain a JSON object."
    assert problem["type"].endswith("/bad-request")


@pytest.mark.parametrize("body", ['{"unterminated": ', "not json at all", "[1, 2, 3]", '"a string"'])
def test_body_that_is_not_a_json_object_returns_400(
    api_gateway_event: EventFactory,
    lambda_context: FakeLambdaContext,
    body: str,
) -> None:
    """Malformed JSON and non-object JSON both fail structural validation."""
    response = _invoke(api_gateway_event(body=body), lambda_context)

    assert response["statusCode"] == HTTPStatus.BAD_REQUEST
    problem = _body(response)
    assert problem["title"] == "Malformed Event"
    assert problem["detail"]


def test_rejected_event_is_logged_and_counted(
    api_gateway_event: EventFactory,
    lambda_context: FakeLambdaContext,
    captured_output: OutputReader,
) -> None:
    """Rejections are warned about with full context and counted as a metric."""
    _invoke(api_gateway_event(body=""), lambda_context)

    output = captured_output()
    record = output.log_with_message("Event rejected")
    assert record["level"] == "WARNING"
    assert record["reason"] == "EmptyBodyError"
    assert record["status"] == HTTPStatus.BAD_REQUEST
    assert record["source_ip"] == TEST_SOURCE_IP
    assert handler_module.METRIC_EVENTS_REJECTED in output.metric_names()


def test_unexpected_errors_propagate_for_dlq_handling(
    api_gateway_event: EventFactory,
    lambda_context: FakeLambdaContext,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Only client errors are caught, so unrecoverable failures reach the DLQ."""

    def _explode(event: dict[str, Any]) -> None:
        raise RuntimeError("kinesis unavailable")

    monkeypatch.setattr(handler_module, "parse_request", _explode)

    with pytest.raises(RuntimeError, match="kinesis unavailable"):
        _invoke(api_gateway_event(), lambda_context)
