"""Current-account disable protection error."""

from __future__ import annotations

from application.errors.invalid_operation import InvalidOperationError


class CurrentAccountDisableForbidden(InvalidOperationError):
    """Authenticated master attempted to disable its own account."""

    error_code = "AUTH_CURRENT_ACCOUNT_DISABLE_FORBIDDEN"
    public_message = "Current account cannot be disabled."
