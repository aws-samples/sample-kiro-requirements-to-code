"""Ingestion Lambda for ``POST /events``.

Deployed with the ``src/functions`` directory as the package root, so the
configured Lambda handler is ``ingest.handler.handler``. Keeping the function as
a package lets the modules below use relative imports without shadowing the
top-level modules provided by the ``common`` layer on ``/opt/python``.
"""
