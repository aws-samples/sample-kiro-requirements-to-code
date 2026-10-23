"""Ingestion Lambda: accept events over HTTPS and acknowledge them.

Story E1 of feature 101. The handler validates the request envelope, assigns a
UUIDv7 correlation ID and returns ``202 Accepted``. Schema validation (E2) and
Kinesis persistence (E3) plug into the same handler later.
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from datetime import UTC, datetime
from http import HTTPStatus
from typing import Any, Final

from aws_lambda_powertools.logging import correlation_paths
from aws_lambda_powertools.metrics import MetricUnit
from aws_lambda_powertools.utilities.typing import LambdaContext
from pydantic import ValidationError
from uuid_extensions import uuid7str

from config import CONFIG, logger, metrics, tracer
from responses import JSON_CONTENT_TYPE, json_response

from .exceptions import EmptyBodyError, IngestError, MalformedEventError, UnsupportedMediaTypeError
from .models import IngestRequest, IngestResponse, RequestMetadata

METRIC_EVENTS_RECEIVED: Final[str] = "EventsReceived"
METRIC_EVENTS_INGESTED: Final[str] = "EventsIngested"
METRIC_EVENTS_REJECTED: Final[str] = "EventsRejected"
METRIC_EVENT_SIZE: Final[str] = "EventSizeBytes"
UNKNOWN_SOURCE_IP: Final[str] = "unknown"
DEFAULT_PATH: Final[str] = "/events"


def _header(event: Mapping[str, Any], name: str) -> str | None:
    """Look up a request header, case-insensitively.

    Args:
        event: API Gateway REST proxy event.
        name: Header name to find, in any casing.

    Returns:
        The header value, or ``None`` when the header is absent.
    """
    headers: Mapping[str, Any] = event.get("headers") or {}
    wanted = name.lower()
    for key, value in headers.items():
        if key.lower() == wanted and value is not None:
            return str(value)
    return None


def _is_json_content_type(content_type: str) -> bool:
    """Check whether a ``Content-Type`` header declares JSON.

    Args:
        content_type: Raw header value, possibly with parameters such as
            ``; charset=utf-8``.

    Returns:
        ``True`` when the media type is ``application/json``.
    """
    media_type = content_type.split(";", maxsplit=1)[0].strip().lower()
    return media_type == JSON_CONTENT_TYPE


def _api_request_id(event: Mapping[str, Any]) -> str | None:
    """Return the API Gateway request ID, when the event carries one.

    Args:
        event: API Gateway REST proxy event.

    Returns:
        The request ID, or ``None`` when it is absent.
    """
    request_context: Mapping[str, Any] = event.get("requestContext") or {}
    request_id = request_context.get("requestId")
    return str(request_id) if request_id else None


def _request_instance(event: Mapping[str, Any]) -> str:
    """Build the Problem Details ``instance`` URI reference for a request.

    Args:
        event: API Gateway REST proxy event.

    Returns:
        The request path, suffixed with the API Gateway request ID when present.
    """
    request_context: Mapping[str, Any] = event.get("requestContext") or {}
    path = str(request_context.get("path") or event.get("path") or DEFAULT_PATH)
    request_id = request_context.get("requestId")
    return f"{path}#{request_id}" if request_id else path


def _build_metadata(event: Mapping[str, Any], *, correlation_id: str) -> RequestMetadata:
    """Extract the structured context logged for every request.

    Args:
        event: API Gateway REST proxy event.
        correlation_id: Correlation ID assigned to this request.

    Returns:
        Metadata covering correlation ID, source IP, timestamp and body size.
    """
    request_context: Mapping[str, Any] = event.get("requestContext") or {}
    identity: Mapping[str, Any] = request_context.get("identity") or {}
    body = event.get("body")
    size_bytes = len(body.encode("utf-8")) if isinstance(body, str) else 0
    return RequestMetadata(
        correlation_id=correlation_id,
        source_ip=str(identity.get("sourceIp") or UNKNOWN_SOURCE_IP),
        received_at=datetime.now(tz=UTC),
        event_size_bytes=size_bytes,
    )


@tracer.capture_method
def parse_request(event: Mapping[str, Any]) -> IngestRequest:
    """Validate the request envelope and decode the body.

    Args:
        event: API Gateway REST proxy event.

    Returns:
        The decoded request body.

    Raises:
        UnsupportedMediaTypeError: The ``Content-Type`` is missing or is not
            ``application/json``.
        EmptyBodyError: The body is missing, empty or whitespace only.
        MalformedEventError: The body is not a JSON object.
    """
    content_type = _header(event, "content-type")
    if content_type is None or not _is_json_content_type(content_type):
        detail = f"Content-Type must be {JSON_CONTENT_TYPE}, received {content_type or 'none'}."
        raise UnsupportedMediaTypeError(detail, extensions={"expected_content_type": JSON_CONTENT_TYPE})

    body = event.get("body")
    if not isinstance(body, str) or not body.strip():
        raise EmptyBodyError("Request body must contain a JSON object.")

    try:
        decoded = json.loads(body)
    except json.JSONDecodeError as error:
        detail = f"Request body is not valid JSON: {error.msg} at line {error.lineno}, column {error.colno}."
        raise MalformedEventError(detail) from error

    if not isinstance(decoded, dict):
        detail = f"Request body must be a JSON object, received a JSON {type(decoded).__name__}."
        raise MalformedEventError(detail)

    try:
        return IngestRequest.model_validate(decoded)
    except ValidationError as error:
        detail = "Request body failed envelope validation."
        raise MalformedEventError(detail, extensions={"errors": error.errors(include_url=False)}) from error


@logger.inject_lambda_context(correlation_id_path=correlation_paths.API_GATEWAY_REST, clear_state=True)
@tracer.capture_lambda_handler
@metrics.log_metrics(capture_cold_start_metric=True)
def handler(event: dict[str, Any], context: LambdaContext) -> dict[str, Any]:
    """Accept an event submitted to ``POST /events`` and acknowledge it.

    Authentication is handled upstream: API Gateway requires an ``x-api-key``
    header and answers ``403 Forbidden`` before this function is invoked.

    Args:
        event: API Gateway REST proxy integration event.
        context: Lambda runtime context.

    Returns:
        ``202 Accepted`` with ``{"correlation_id": ..., "status": "accepted"}``,
        or an RFC 7807 Problem Details response for a rejected request.
    """
    correlation_id = uuid7str()
    metadata = _build_metadata(event, correlation_id=correlation_id)
    # The decorator seeds correlation_id from the API Gateway request ID; the
    # pipeline-wide identifier is the UUIDv7 minted here, so it takes over.
    logger.set_correlation_id(correlation_id)
    logger.append_keys(api_request_id=_api_request_id(event), environment=CONFIG.environment)
    tracer.put_annotation(key="correlation_id", value=correlation_id)
    metrics.add_metric(name=METRIC_EVENTS_RECEIVED, unit=MetricUnit.Count, value=1)

    try:
        request = parse_request(event)
    except IngestError as error:
        metrics.add_metric(name=METRIC_EVENTS_REJECTED, unit=MetricUnit.Count, value=1)
        logger.warning(
            "Event rejected",
            extra={
                **metadata.to_log_context(),
                "reason": type(error).__name__,
                "status": error.status,
                "detail": error.detail,
            },
        )
        return error.to_response(correlation_id=correlation_id, instance=_request_instance(event))

    metrics.add_metric(name=METRIC_EVENTS_INGESTED, unit=MetricUnit.Count, value=1)
    metrics.add_metric(name=METRIC_EVENT_SIZE, unit=MetricUnit.Bytes, value=metadata.event_size_bytes)
    # Story E2 validates request.payload() against the schema registry and E3
    # wraps it in the shared EventEnvelope before writing it to Kinesis.
    logger.info("Event accepted", extra={**metadata.to_log_context(), "payload_fields": len(request.payload())})

    acknowledgement = IngestResponse(correlation_id=correlation_id)
    return json_response(
        status=HTTPStatus.ACCEPTED,
        body=acknowledgement.model_dump(mode="json"),
        correlation_id=correlation_id,
    )
