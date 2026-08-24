"""FastAPI application factory and composition root."""

from __future__ import annotations

from fastapi import FastAPI

from configuration import Settings
from observability import configure_observability, instrument_fastapi

from .errors import configure_exception_handlers
from .lifespan import create_lifespan
from .openapi import API_DESCRIPTION, OPENAPI_TAGS, PokerLostAPI
from .request_context import configure_request_context
from .routes import configure_routes


def create_app(settings: Settings | None = None) -> FastAPI:
    """Build a configured authService application without creating runtime resources."""
    resolved_settings = settings or Settings()
    configure_observability(resolved_settings)
    application = PokerLostAPI(
        title=resolved_settings.application.service_name,
        version=resolved_settings.application.version,
        description=API_DESCRIPTION,
        debug=False,
        lifespan=create_lifespan(resolved_settings),
        openapi_tags=OPENAPI_TAGS,
        openapi_url=None,
        docs_url=None,
        redoc_url=None,
    )

    configure_request_context(application)
    configure_exception_handlers(application)
    configure_routes(application)
    instrument_fastapi(application, resolved_settings)
    return application
