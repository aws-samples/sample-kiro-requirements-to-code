"""Environment-driven configuration and the shared Powertools instances.

Every Lambda function in StreamProcess imports ``logger``, ``tracer`` and
``metrics`` from this module instead of creating its own instances, so that
service name, log level and metric namespace stay consistent across the
pipeline and are driven purely by environment variables.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Final

from aws_lambda_powertools import Logger, Metrics, Tracer

DEFAULT_SERVICE_NAME: Final[str] = "streamprocess-ingest"
DEFAULT_LOG_LEVEL: Final[str] = "INFO"
DEFAULT_ENVIRONMENT: Final[str] = "dev"
METRICS_NAMESPACE_PREFIX: Final[str] = "StreamProcess"
# ISO 8601 UTC, per the data standards in technology-guidelines.md.
# ``%F`` is the Powertools directive for milliseconds.
ISO_8601_DATEFMT: Final[str] = "%Y-%m-%dT%H:%M:%S.%FZ"


@dataclass(frozen=True, slots=True)
class Config:
    """Runtime configuration resolved from the Lambda environment.

    Attributes:
        service_name: Logical service name attached to logs, traces and metrics.
        log_level: Powertools log level, e.g. ``INFO`` or ``DEBUG``.
        environment: Deployment environment such as ``dev`` or ``prod``.
        metrics_namespace: CloudWatch namespace for embedded metrics.
    """

    service_name: str
    log_level: str
    environment: str
    metrics_namespace: str

    @classmethod
    def from_environment(cls) -> Config:
        """Build a configuration object from environment variables.

        Returns:
            A frozen configuration populated from the environment, falling back
            to the module defaults when a variable is not set.
        """
        environment = os.environ.get("ENVIRONMENT", DEFAULT_ENVIRONMENT)
        return cls(
            service_name=os.environ.get("POWERTOOLS_SERVICE_NAME", DEFAULT_SERVICE_NAME),
            log_level=os.environ.get("LOG_LEVEL", DEFAULT_LOG_LEVEL).upper(),
            environment=environment,
            metrics_namespace=os.environ.get(
                "POWERTOOLS_METRICS_NAMESPACE",
                f"{METRICS_NAMESPACE_PREFIX}/{environment}",
            ),
        )


CONFIG: Final[Config] = Config.from_environment()

logger: Final[Logger] = Logger(
    service=CONFIG.service_name,
    level=CONFIG.log_level,
    utc=True,
    datefmt=ISO_8601_DATEFMT,
)
tracer: Final[Tracer] = Tracer(service=CONFIG.service_name)
metrics: Final[Metrics] = Metrics(namespace=CONFIG.metrics_namespace, service=CONFIG.service_name)
