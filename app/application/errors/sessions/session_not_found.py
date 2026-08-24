"""Owned session not-found error."""

from __future__ import annotations

from application.errors.not_found import NotFoundError


class SessionNotFound(NotFoundError):
    """Requested session does not exist within the authenticated principal boundary."""

    error_code = "AUTH_SESSION_NOT_FOUND"
    public_message = "SessionModel not found."
