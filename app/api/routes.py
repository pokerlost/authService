"""Top-level API router registration."""

from __future__ import annotations

from fastapi import FastAPI

from .routers.health import router as health_router


def configure_routes(application: FastAPI) -> None:
    """Register all public routers on the application."""
    application.include_router(health_router)
