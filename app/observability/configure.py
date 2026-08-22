"""Central Logfire configuration and instrumentation."""

from __future__ import annotations

from typing import Any

import logfire
from fastapi import FastAPI, Request, WebSocket
from sqlalchemy.ext.asyncio import AsyncEngine

from configuration import Settings

_SENSITIVE_PATTERNS = (
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


def _discard_endpoint_arguments(
    _request: Request | WebSocket,
    _attributes: dict[str, Any],
) -> dict[str, Any]:
    return {}


def configure_observability(settings: Settings) -> None:
    """Configure process-wide Logfire before creating the application."""
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
        scrubbing=logfire.ScrubbingOptions(extra_patterns=_SENSITIVE_PATTERNS),
    )


def instrument_application(application: FastAPI) -> None:
    """Instrument FastAPI without capturing headers or endpoint arguments."""
    logfire.instrument_fastapi(
        application,
        capture_headers=False,
        request_attributes_mapper=_discard_endpoint_arguments,
    )


def instrument_database(engine: AsyncEngine) -> None:
    """Instrument the concrete lifespan-owned SQLAlchemy engine."""
    logfire.instrument_sqlalchemy(engine=engine)
