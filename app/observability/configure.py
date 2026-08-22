"""Central Logfire configuration and instrumentation."""

from __future__ import annotations

from typing import Any

import logfire
from fastapi import FastAPI, Request, WebSocket
from sqlalchemy.ext.asyncio import AsyncEngine

from configuration import Settings

SENSITIVE_PATTERNS = (
    r"authorization",
    r"cookie",
    r"password",
    r"access[._ -]?token",
    r"refresh[._ -]?token",
    r"reset[._ -]?token",
    r"private[._ -]?key",
    r"client[._ -]?secret",
    r"database[._ -]?url",
    r"dsn",
)

def configure_observability(
    *,
    application: FastAPI,
    engine: AsyncEngine,
    settings: Settings,
) -> None:
    """Configure Logfire once and instrument FastAPI and SQLAlchemy."""
    logfire_settings = settings.logfire
    token = (
        logfire_settings.token.get_secret_value() if logfire_settings.token is not None else None
    )
    logfire.configure(
        send_to_logfire=logfire_settings.send_to_logfire,
        token=token,
        service_name=settings.application.service_name,
        service_version=settings.application.version,
        environment=settings.application.environment.value,
        console=None if logfire_settings.console_enabled else False,
        scrubbing=logfire.ScrubbingOptions(extra_patterns=SENSITIVE_PATTERNS),
    )
    logfire.instrument_fastapi(
        application,
        capture_headers=False,
    )
    logfire.instrument_sqlalchemy(engine=engine)
