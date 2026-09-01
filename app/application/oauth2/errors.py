"""Safe internal getToken failure vocabulary."""

from __future__ import annotations

from enum import StrEnum


class GetTokenErrorCode(StrEnum):
    """Closed internal categories mapped to stable authService application errors."""

    INVALID_REQUEST = "invalid_request"
    INVALID_CLIENT = "invalid_client"
    UNAUTHORIZED_CLIENT = "unauthorized_client"
    INVALID_SCOPE = "invalid_scope"
    INVALID_TARGET = "invalid_target"
    TEMPORARILY_UNAVAILABLE = "temporarily_unavailable"
    SERVER_ERROR = "server_error"


class GetTokenError(Exception):
    """Expected getToken failure carrying only a safe closed error code."""

    __slots__ = ("error",)

    def __init__(self, error: GetTokenErrorCode) -> None:
        """Store one public error code without retaining submitted input."""
        super().__init__()
        self.error = error
