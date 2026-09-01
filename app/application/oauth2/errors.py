"""Safe internal token-operation failure vocabulary."""

from __future__ import annotations

from enum import StrEnum


class OAuth2ErrorCode(StrEnum):
    """Closed internal categories mapped to stable authService application errors."""

    INVALID_REQUEST = "invalid_request"
    UNSUPPORTED_GRANT_TYPE = "unsupported_grant_type"
    INVALID_CLIENT = "invalid_client"
    UNAUTHORIZED_CLIENT = "unauthorized_client"
    INVALID_SCOPE = "invalid_scope"
    INVALID_TARGET = "invalid_target"
    TEMPORARILY_UNAVAILABLE = "temporarily_unavailable"
    SERVER_ERROR = "server_error"


class OAuth2TokenError(Exception):
    """Expected OAuth2 failure carrying only a safe closed error code."""

    __slots__ = ("error",)

    def __init__(self, error: OAuth2ErrorCode) -> None:
        """Store one public error code without retaining submitted input."""
        super().__init__()
        self.error = error
