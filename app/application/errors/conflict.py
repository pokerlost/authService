"""Application conflict error category."""

from __future__ import annotations

from .base import ApplicationError


class ConflictError(ApplicationError):
    """Requested state conflicts with existing application state."""

    error_code = "AUTH_CONFLICT"
    public_message = "The requested operation conflicts with existing state."
