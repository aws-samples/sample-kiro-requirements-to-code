"""Fixtures for the ingestion Lambda tests.

Everything here runs offline: no boto3 client is created, no AWS credentials are
read and tracing is disabled, so the suite never touches a real account.
"""

from __future__ import annotations

import io
import json
import os
from collections.abc import Callable, Iterator, Mapping
from dataclasses import dataclass, field
from typing import Any, Final

import pytest

# Powertools and the X-Ray SDK read the environment at import time, so it is
# prepared before the shared layer and the handler are imported below.
#
# Any profile or credentials in the ambient environment are replaced with
# obvious dummies, because the suite must never be able to reach an AWS account.
# LAMBDA_TASK_ROOT makes the X-Ray SDK fall back to its local sampler instead of
# building an X-Ray client, and tracing is disabled on top of that.
os.environ.pop("AWS_PROFILE", None)
os.environ.pop("AWS_DEFAULT_PROFILE", None)
os.environ["AWS_ACCESS_KEY_ID"] = "dummy-access-key-id"
os.environ["AWS_SECRET_ACCESS_KEY"] = "dummy-secret-access-key"  # noqa: S105
os.environ["AWS_SESSION_TOKEN"] = "dummy-session-token"  # noqa: S105
os.environ["AWS_DEFAULT_REGION"] = "us-east-1"
os.environ["AWS_REGION"] = "us-east-1"
os.environ["LAMBDA_TASK_ROOT"] = "/var/task"
os.environ["AWS_XRAY_SDK_ENABLED"] = "false"
os.environ["AWS_XRAY_CONTEXT_MISSING"] = "IGNORE_ERROR"
os.environ["POWERTOOLS_TRACE_DISABLED"] = "true"
os.environ["POWERTOOLS_LOG_DEDUPLICATION_DISABLED"] = "true"
os.environ.setdefault("POWERTOOLS_SERVICE_NAME", "streamprocess-ingest")
os.environ.setdefault("POWERTOOLS_METRICS_NAMESPACE", "StreamProcess/test")
os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("LOG_LEVEL", "INFO")

from config import logger, metrics

TEST_SOURCE_IP: Final[str] = "203.0.113.42"
TEST_API_KEY: Final[str] = "unit-test-api-key"
TEST_ACCOUNT_ID: Final[str] = "123456789012"
TEST_FUNCTION_NAME: Final[str] = "streamprocess-test-ingest-api"


@dataclass(frozen=True)
class FakeLambdaContext:
    """Stand-in for the Lambda runtime context object."""

    function_name: str = TEST_FUNCTION_NAME
    function_version: str = "$LATEST"
    invoked_function_arn: str = f"arn:aws:lambda:us-east-1:{TEST_ACCOUNT_ID}:function:{TEST_FUNCTION_NAME}"
    memory_limit_in_mb: int = 256
    aws_request_id: str = "8f2c0c4e-0b64-4f1a-9f0f-1f9a6f4d3c21"
    log_group_name: str = f"/aws/lambda/{TEST_FUNCTION_NAME}"
    log_stream_name: str = "2025/01/15/[$LATEST]0123456789abcdef"

    def get_remaining_time_in_millis(self) -> int:
        """Report the remaining execution budget.

        Returns:
            A fixed budget, in milliseconds.
        """
        return 30_000


@dataclass(frozen=True)
class CapturedOutput:
    """Structured log records and EMF metric documents emitted by a handler."""

    logs: list[dict[str, Any]] = field(default_factory=list)
    metrics: list[dict[str, Any]] = field(default_factory=list)

    def log_with_message(self, message: str) -> dict[str, Any]:
        """Return the single log record carrying ``message``.

        Args:
            message: Exact log message to look for.

        Returns:
            The matching log record.

        Raises:
            AssertionError: No record, or more than one record, matched.
        """
        matches = [record for record in self.logs if record.get("message") == message]
        assert len(matches) == 1, f"expected exactly one {message!r} log record, found {len(matches)}"
        return matches[0]

    def metric_names(self) -> set[str]:
        """Collect the metric names published across all EMF documents.

        Returns:
            Every metric name found in the captured EMF documents.
        """
        names: set[str] = set()
        for document in self.metrics:
            for metric_directive in document.get("_aws", {}).get("CloudWatchMetrics", []):
                names.update(metric["Name"] for metric in metric_directive.get("Metrics", []))
        return names


def _json_documents(raw: str) -> list[dict[str, Any]]:
    """Parse newline-delimited JSON, ignoring blank and non-object lines.

    Args:
        raw: Captured stream contents.

    Returns:
        Every line that parsed into a JSON object.
    """
    documents: list[dict[str, Any]] = []
    for line in raw.splitlines():
        candidate = line.strip()
        if not candidate.startswith("{"):
            continue
        parsed = json.loads(candidate)
        if isinstance(parsed, dict):
            documents.append(parsed)
    return documents


@pytest.fixture
def lambda_context() -> FakeLambdaContext:
    """Provide a fake Lambda context.

    Returns:
        A context object exposing the attributes Powertools reads.
    """
    return FakeLambdaContext()


@pytest.fixture(autouse=True)
def _reset_metrics() -> Iterator[None]:
    """Clear the Powertools metric singleton around every test.

    Yields:
        Control to the test.
    """
    metrics.clear_metrics()
    yield
    metrics.clear_metrics()


@pytest.fixture
def captured_output(capsys: pytest.CaptureFixture[str]) -> Iterator[Callable[[], CapturedOutput]]:
    """Capture Powertools log records and EMF metric documents.

    The logger's stream handler is rebound to an in-memory buffer because it
    holds a reference to the stdout object that existed at import time, which
    ``capsys`` does not intercept. EMF metrics are printed at flush time, so
    those are read from ``capsys``.

    Args:
        capsys: Pytest stdout/stderr capture fixture.

    Yields:
        A callable that parses everything captured so far.
    """
    buffer = io.StringIO()
    handler = logger.registered_handler
    original_stream = handler.stream
    handler.setStream(buffer)
    try:
        yield lambda: CapturedOutput(
            logs=_json_documents(buffer.getvalue()),
            metrics=[document for document in _json_documents(capsys.readouterr().out) if "_aws" in document],
        )
    finally:
        handler.setStream(original_stream)


@pytest.fixture
def api_gateway_event() -> Callable[..., dict[str, Any]]:
    """Build API Gateway REST proxy integration events.

    Returns:
        A factory accepting ``body``, ``content_type``, ``api_key``,
        ``source_ip``, ``path`` and extra ``headers``.
    """

    def _build(
        *,
        body: str | None = '{"event_type": "order.created", "order_id": "A-1001"}',
        content_type: str | None = "application/json",
        api_key: str | None = TEST_API_KEY,
        source_ip: str = TEST_SOURCE_IP,
        path: str = "/events",
        headers: Mapping[str, str] | None = None,
    ) -> dict[str, Any]:
        request_headers: dict[str, str] = {"Host": "api.example.com", "User-Agent": "pytest"}
        if content_type is not None:
            request_headers["Content-Type"] = content_type
        if api_key is not None:
            request_headers["x-api-key"] = api_key
        if headers:
            request_headers.update(headers)
        return {
            "resource": path,
            "path": path,
            "httpMethod": "POST",
            "headers": request_headers,
            "multiValueHeaders": {key: [value] for key, value in request_headers.items()},
            "queryStringParameters": None,
            "pathParameters": None,
            "stageVariables": None,
            "requestContext": {
                "resourceId": "abc123",
                "resourcePath": path,
                "httpMethod": "POST",
                "path": f"/v1{path}",
                "accountId": TEST_ACCOUNT_ID,
                "apiId": "0123456789",
                "stage": "v1",
                "requestId": "1c8f4b6e-9a1d-4f8f-9d2f-0a1b2c3d4e5f",
                "requestTimeEpoch": 1_736_936_400_000,
                "identity": {
                    "sourceIp": source_ip,
                    "userAgent": "pytest",
                    "apiKey": api_key,
                    "apiKeyId": "key-0123456789" if api_key else None,
                },
            },
            "body": body,
            "isBase64Encoded": False,
        }

    return _build
