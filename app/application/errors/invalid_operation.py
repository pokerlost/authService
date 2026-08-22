"""Invalid application operation error category."""

from __future__ import annotations

from .base import ApplicationError


class InvalidOperationError(ApplicationError):
    """Requested transition or operation is not allowed."""

    error_code = "AUTH_INVALID_OPERATION"
    public_message = "The requested operation is not allowed."
