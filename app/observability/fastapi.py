"""Privacy-safe FastAPI Logfire instrumentation."""

from __future__ import annotations

import logfire
from fastapi import FastAPI

from configuration import Settings


def instrument_fastapi(app: FastAPI, settings: Settings) -> None:
    """Instrument route timing without recording headers or parsed arguments."""
    if not settings.logfire.enabled:
        return

    logfire.instrument_fastapi(
        app,
        capture_headers=False,
        record_send_receive=False,
        extra_spans=False,
    )
