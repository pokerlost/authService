"""Invalid explicit OAuth2 scope grant error."""

from __future__ import annotations

from .invalid_operation import InvalidOperationError


class ScopeGrantInvalidError(InvalidOperationError):
    """Requested role or service scope grant violates ownership or activity rules."""

    error_code = "AUTH_SCOPE_GRANT_INVALID"
    public_message = "The requested scope grant is not valid."
