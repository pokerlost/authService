"""Duplicate human authentication username error."""

from __future__ import annotations

from application.errors import ConflictError


class UsernameAlreadyRegistered(ConflictError):
    """Canonical username already belongs to a human account."""

    error_code = "AUTH_USERNAME_ALREADY_REGISTERED"
    public_message = "Username is already registered."
