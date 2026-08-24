"""Invalid current password error."""

from __future__ import annotations

from application.errors.invalid_operation import InvalidOperationError


class CurrentPasswordInvalidError(InvalidOperationError):
    """Authenticated human supplied an incorrect current password."""

    error_code = "AUTH_CURRENT_PASSWORD_INVALID"
    public_message = "Current password is invalid."
