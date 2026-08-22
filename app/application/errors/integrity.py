"""Application integrity failure category."""

from __future__ import annotations

from .base import ApplicationError


class IntegrityError(ApplicationError):
    """Internal application invariant could not be preserved."""

    error_code = "AUTH_INTEGRITY_ERROR"
    public_message = "Application integrity validation failed."
