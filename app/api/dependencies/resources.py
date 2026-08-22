"""Runtime resource dependency."""

from __future__ import annotations

from fastapi import Request

from api.resources import ApplicationResources


def get_application_resources(request: Request) -> ApplicationResources:
    """Return resources attached by the application lifespan."""
    resources = request.app.state.resources
    if not isinstance(resources, ApplicationResources):
        raise RuntimeError("Application resources are not initialized")
    return resources
