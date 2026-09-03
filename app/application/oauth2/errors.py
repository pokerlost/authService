"""Safe application failures for token issuance."""

from __future__ import annotations

from typing import ClassVar

from application.errors import (
    ApplicationError,
    InvalidRequestError,
)
from service import SERVICE_ERROR_PREFIX


class InvalidOAuthClientError(ApplicationError):
    """OAuth client identity or credential authentication failed."""

    error_code: ClassVar[str] = f"{SERVICE_ERROR_PREFIX}_INVALID_CLIENT"
    public_message: ClassVar[str] = "Client authentication failed."


class UnauthorizedOAuthClientError(InvalidRequestError):
    """The authenticated client may not use the requested grant."""

    error_code: ClassVar[str] = f"{SERVICE_ERROR_PREFIX}_UNAUTHORIZED_CLIENT"
    public_message: ClassVar[str] = "The authenticated client is not authorized to request a token."


class InvalidRequestedScopeError(InvalidRequestError):
    """The requested scopes are absent, duplicated, unknown, or not granted."""

    error_code: ClassVar[str] = f"{SERVICE_ERROR_PREFIX}_INVALID_SCOPE"
    public_message: ClassVar[str] = "The requested scope is invalid."


class InvalidTargetAudienceError(InvalidRequestError):
    """The requested exact service audience is unknown or not granted."""

    error_code: ClassVar[str] = f"{SERVICE_ERROR_PREFIX}_INVALID_TARGET"
    public_message: ClassVar[str] = "The requested audience is invalid."
