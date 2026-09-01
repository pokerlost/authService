"""Top-level API router registration."""

from __future__ import annotations

from fastapi import FastAPI

from configuration import Settings

from .routers.get_token import create_get_token_router
from .routers.openapi_document import create_openapi_document_router
from .routers.root import create_root_router


def configure_routes(application: FastAPI, settings: Settings) -> None:
    """Register settings-aware template baseline routers."""
    application.include_router(
        create_root_router(
            operation=settings.root_operation,
        )
    )
    application.include_router(
        create_openapi_document_router(
            application=application,
            operation=settings.openapi_operation,
        )
    )
    application.include_router(create_get_token_router())
