"""FastAPI application factory and composition root."""

from __future__ import annotations

from fastapi import FastAPI

from configuration import Settings
from observability import configure_observability

from .errors import configure_exception_handlers
from .lifespan import create_lifespan
from .request_context import configure_request_context
from .resources import create_application_resources
from .routes import configure_routes


def create_application(settings: Settings | None = None) -> FastAPI:
    """Build a fully configured authService ASGI application."""
    resolved_settings = settings or Settings()
    resources = create_application_resources(resolved_settings)
    openapi_enabled = resolved_settings.http.openapi_enabled

    application = FastAPI(
        title=resolved_settings.application.service_name,
        version=resolved_settings.application.version,
        description=(
            "PokerLost centralized identity, authentication, and coarse-grained "
            "authorization service."
        ),
        debug=False,
        lifespan=create_lifespan(resources),
        openapi_url="/openapi.json" if openapi_enabled else None,
        docs_url="/docs" if openapi_enabled else None,
        redoc_url=None,
    )
    application.state.resources = resources

    configure_request_context(application)
    configure_exception_handlers(application)
    configure_routes(application)

    openapi_schema = application.openapi()
    openapi_schema["x-pokerlost-service"] = {
        "id": resolved_settings.application.service_name,
    }
    application.openapi_schema = openapi_schema

    configure_observability(
        application=application,
        engine=resources.engine,
        settings=resolved_settings,
    )
    return application
