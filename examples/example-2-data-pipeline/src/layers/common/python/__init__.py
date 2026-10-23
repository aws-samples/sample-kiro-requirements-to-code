"""Shared code for the StreamProcess ``common`` Lambda layer.

The layer archive is built from ``src/layers/common`` so that this directory
lands on ``/opt/python`` at runtime, which the Lambda runtime already places on
``sys.path``. Consumers therefore import the modules as top-level modules::

    from config import CONFIG, logger, metrics, tracer
    from responses import problem_response
    from models import EventEnvelope

This file exists so the directory is also importable by local tooling; it
intentionally re-exports nothing, because at runtime the modules below are not
part of a package.
"""
