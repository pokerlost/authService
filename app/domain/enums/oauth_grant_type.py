"""OAuth2 grant type vocabulary."""

from __future__ import annotations

from enum import StrEnum


class OAuthGrantType(StrEnum):
    """Closed grant types recognized by authService."""

    CLIENT_CREDENTIALS = "client_credentials"
    REFRESH_TOKEN = "refresh_token"
    LOGIN_GRANT = "urn:pokerlost:params:oauth:grant-type:login-grant"
