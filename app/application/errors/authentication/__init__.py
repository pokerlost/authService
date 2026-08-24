"""Authentication failure facade."""

from __future__ import annotations

from .base import AuthenticationError
from .current_password_invalid import CurrentPasswordInvalidError
from .invalid_access_token import InvalidAccessToken
from .invalid_credentials import InvalidCredentials
from .invalid_oauth_client import InvalidOAuthClient
from .invalid_oauth_grant import InvalidOAuthGrant
from .invalid_oauth_scope import InvalidOAuthScope
from .invalid_refresh_token import InvalidRefreshToken
from .unsupported_oauth_grant import UnsupportedOAuthGrantType

__all__ = (
    "AuthenticationError",
    "CurrentPasswordInvalidError",
    "InvalidAccessToken",
    "InvalidCredentials",
    "InvalidOAuthClient",
    "InvalidOAuthGrant",
    "InvalidOAuthScope",
    "InvalidRefreshToken",
    "UnsupportedOAuthGrantType",
)
