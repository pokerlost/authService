"""Support-safe ordinary-user lookup error."""

from __future__ import annotations

from application.errors.not_found import NotFoundError


class UserAccountNotFound(NotFoundError):
    """Canonical username does not identify an ordinary-user account."""

    error_code = "AUTH_USER_ACCOUNT_NOT_FOUND"
    public_message = "User account not found."
