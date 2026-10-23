"""Shared Pydantic models used across the StreamProcess pipeline."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from typing import Any, Final

from pydantic import BaseModel, ConfigDict, Field, field_serializer

SOURCE_API: Final[str] = "api"


def utc_now() -> datetime:
    """Return the current time as a timezone-aware UTC timestamp.

    Returns:
        The current UTC time.
    """
    return datetime.now(tz=UTC)


class EventEnvelope(BaseModel):
    """Canonical envelope wrapped around every event entering the pipeline.

    The envelope is what downstream stages (Kinesis records, DLQ messages,
    S3 objects) carry, so the payload can be traced end to end by
    ``correlation_id`` without inspecting publisher-specific fields.

    Attributes:
        correlation_id: UUIDv7 assigned at ingestion time.
        source: Ingestion channel, e.g. ``api``.
        received_at: Timestamp the event was accepted, ISO 8601 UTC.
        size_bytes: Size of the raw payload as received, in bytes.
        payload: The publisher-supplied event body.
        schema_name: Registered schema the payload was validated against, when
            known. Schema validation itself arrives with story E2.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    correlation_id: str = Field(min_length=1)
    source: str = Field(min_length=1)
    received_at: datetime
    size_bytes: int = Field(ge=0)
    payload: dict[str, Any]
    schema_name: str | None = None

    @field_serializer("received_at")
    def _serialize_received_at(self, value: datetime) -> str:
        """Serialise timestamps as ISO 8601 UTC with a trailing ``Z``.

        Args:
            value: The timestamp to serialise.

        Returns:
            An ISO 8601 string in UTC, e.g. ``2025-01-15T10:30:00Z``.
        """
        return value.astimezone(UTC).isoformat().replace("+00:00", "Z")

    @classmethod
    def wrap(
        cls,
        *,
        correlation_id: str,
        payload: dict[str, Any],
        source: str = SOURCE_API,
        size_bytes: int | None = None,
        schema_name: str | None = None,
        received_at: datetime | None = None,
    ) -> EventEnvelope:
        """Wrap a decoded payload in an envelope.

        Args:
            correlation_id: UUIDv7 assigned at ingestion time.
            payload: The publisher-supplied event body.
            source: Ingestion channel.
            size_bytes: Raw payload size. Computed from ``payload`` when omitted.
            schema_name: Registered schema name, when known.
            received_at: Acceptance timestamp. Defaults to now, in UTC.

        Returns:
            A populated, immutable envelope.
        """
        if size_bytes is None:
            size_bytes = len(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
        return cls(
            correlation_id=correlation_id,
            source=source,
            received_at=received_at if received_at is not None else utc_now(),
            size_bytes=size_bytes,
            payload=payload,
            schema_name=schema_name,
        )
