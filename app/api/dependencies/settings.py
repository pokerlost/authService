"""Application settings dependency."""

from __future__ import annotations

from fastapi import Request

from configuration import Settings


def get_settings(request: Request) -> Settings:
    """Return settings attached separately by the application lifespan."""
    settings = request.app.state.settings
    if not isinstance(settings, Settings):
        raise RuntimeError("Application settings are not initialized")
    return settings
