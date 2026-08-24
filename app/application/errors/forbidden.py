"""Authenticated operation authorization failure."""

from __future__ import annotations

from .base import ApplicationError


class ForbiddenError(ApplicationError):
    """Authenticated principal is not authorized for the requested operation."""

    error_code = "AUTH_FORBIDDEN"
    public_message = "Operation is not allowed."
