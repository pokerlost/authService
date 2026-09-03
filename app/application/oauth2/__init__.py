"""OAuth client application operations and protocol-safe failures."""

from __future__ import annotations

from .errors import (
    InvalidOAuthClientError,
    InvalidRequestedScopeError,
    InvalidTargetAudienceError,
    UnauthorizedOAuthClientError,
)

__all__ = (
    "InvalidOAuthClientError",
    "InvalidRequestedScopeError",
    "InvalidTargetAudienceError",
    "UnauthorizedOAuthClientError",
)
