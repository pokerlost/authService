"""Shared API dependency alias facade."""

from __future__ import annotations

from .database import DatabaseSession
from .oauth2 import (
    IssueClientCredentialsTokenHandlerDep,
    OAuthClientAuthentication,
    OAuthTokenProtocolInput,
)
from .resources import (
    ApplicationResourcesDep,
    BusinessOperationFingerprinterDep,
    ServiceAccessTokenSignerDep,
)
from .settings import SettingsDep

__all__ = (
    "ApplicationResourcesDep",
    "BusinessOperationFingerprinterDep",
    "DatabaseSession",
    "IssueClientCredentialsTokenHandlerDep",
    "OAuthClientAuthentication",
    "OAuthTokenProtocolInput",
    "ServiceAccessTokenSignerDep",
    "SettingsDep",
)
