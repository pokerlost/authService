"""OAuth2 insufficient scope authorization error."""

from __future__ import annotations

from .forbidden import ForbiddenError


class InsufficientScopeError(ForbiddenError):
    """Valid access token lacks one explicitly required operation scope."""

    error_code = "AUTH_INSUFFICIENT_SCOPE"
    public_message = "Access token has insufficient scope."
