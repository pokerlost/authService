"""Closed domain and platform category facade."""

from __future__ import annotations

from .environment import Environment
from .oauth_client_credential_status import OAuthClientCredentialStatus
from .oauth_client_status import OAuthClientStatus
from .oauth_client_type import OAuthClientType
from .oauth_grant_type import OAuthGrantType
from .scopes import Scopes, scope_descriptions

__all__ = (
    "Environment",
    "OAuthClientCredentialStatus",
    "OAuthClientStatus",
    "OAuthClientType",
    "OAuthGrantType",
    "Scopes",
    "scope_descriptions",
)
