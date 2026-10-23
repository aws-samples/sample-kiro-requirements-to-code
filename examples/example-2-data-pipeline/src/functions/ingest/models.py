"""Request and response models for the ingestion endpoint."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_serializer

ACCEPTED_STATUS: Literal["accepted"] = "accepted"


class IngestRequest(BaseModel):
    """Body accepted by ``POST /events``.

    PI 1 performs structural validation only: the body must be a JSON object.
    Validation against registered schemas arrives with story E2, so unknown
    keys are preserved rather than rejected.
    """

    model_config = ConfigDict(extra="allow")

    def payload(self) -> dict[str, Any]:
        """Return the request body as a plain dictionary.

        Returns:
            The publisher-supplied fields, including unknown ones.
        """
        return self.model_dump(mode="json")


class IngestResponse(BaseModel):
    """Acknowledgement returned with HTTP 202.

    Attributes:
        correlation_id: UUIDv7 the publisher uses to trace the event.
        status: Constant ``accepted`` acknowledgement marker.
    """

    model_config = ConfigDict(frozen=True)

    correlation_id: str = Field(min_length=1)
    status: Literal["accepted"] = ACCEPTED_STATUS


class RequestMetadata(BaseModel):
    """Structured context logged and traced for every request.

    ``received_at`` is the ingestion timestamp carried into the event envelope.
    It is deliberately not called ``timestamp``: that key is reserved by the
    Powertools log formatter, which already stamps every record in ISO 8601 UTC.

    Attributes:
        correlation_id: UUIDv7 assigned to this request.
        source_ip: Caller IP reported by API Gateway.
        received_at: Time the request was handled, ISO 8601 UTC.
        event_size_bytes: Size of the raw request body in bytes.
    """

    model_config = ConfigDict(frozen=True)

    correlation_id: str = Field(min_length=1)
    source_ip: str
    received_at: datetime
    event_size_bytes: int = Field(ge=0)

    @field_serializer("received_at")
    def _serialize_received_at(self, value: datetime) -> str:
        """Serialise the timestamp as ISO 8601 UTC with a trailing ``Z``.

        Args:
            value: The timestamp to serialise.

        Returns:
            An ISO 8601 string in UTC, e.g. ``2025-01-15T10:30:00Z``.
        """
        return value.astimezone(UTC).isoformat().replace("+00:00", "Z")

    def to_log_context(self) -> dict[str, Any]:
        """Render the metadata as keys for a structured log entry.

        Returns:
            A JSON-serialisable mapping of log keys.
        """
        return self.model_dump(mode="json")
