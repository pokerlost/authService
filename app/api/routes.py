"""Top-level API router registration."""

from __future__ import annotations

from fastapi import FastAPI

from .routers import get_token, openapi, root


def configure_routes(application: FastAPI) -> None:
    """Register the service routers."""
    application.include_router(root.router)
    application.include_router(openapi.router)
    application.include_router(get_token.router)
