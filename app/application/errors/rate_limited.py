"""Authentication rate-limit error."""

from __future__ import annotations

from .base import ApplicationError


class RateLimitedError(ApplicationError):
    """Authentication attempt key is temporarily locked."""

    error_code = "AUTH_RATE_LIMITED"
    public_message = "Authentication attempts are temporarily rate limited."
