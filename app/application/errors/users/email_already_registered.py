"""Duplicate registered email conflict."""

from __future__ import annotations

from application.errors import ConflictError


class EmailAlreadyRegistered(ConflictError):
    """Normalized human account email already belongs to a principal."""

    error_code = "AUTH_EMAIL_ALREADY_REGISTERED"
    public_message = "An account with this email already exists."
