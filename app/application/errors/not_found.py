"""Application resource-not-found error category."""

from __future__ import annotations

from .base import ApplicationError


class NotFoundError(ApplicationError):
    """Requested application resource does not exist."""

    error_code = "AUTH_NOT_FOUND"
    public_message = "The requested resource was not found."
