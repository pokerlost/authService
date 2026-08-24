"""Master self-reset prohibition."""

from __future__ import annotations

from application.errors.invalid_operation import InvalidOperationError


class SelfPasswordResetForbidden(InvalidOperationError):
    """Master-assisted reset cannot target the authenticated actor."""

    error_code = "AUTH_SELF_PASSWORD_RESET_FORBIDDEN"
    public_message = "Use account password change for the current principal."
