"""Registered service not found error."""

from __future__ import annotations

from application.errors.not_found import NotFoundError


class RegisteredServiceNotFoundError(NotFoundError):
    """Requested PokerLost registry service does not exist."""

    error_code = "AUTH_REGISTERED_SERVICE_NOT_FOUND"
    public_message = "Registered service not found."
