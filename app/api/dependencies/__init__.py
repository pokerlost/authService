"""Shared API dependency alias facade."""

from __future__ import annotations

from .authorization import (
    PokerlostTokenVerifierDep,
    authorize_pokerlost_request,
)
from .database import DatabaseSession
from .get_token import IssueClientCredentialsTokenHandlerDep
from .resources import (
    ApplicationResourcesDep,
    ServiceAccessTokenSignerDep,
)
from .settings import SettingsDep

__all__ = (
    "ApplicationResourcesDep",
    "DatabaseSession",
    "IssueClientCredentialsTokenHandlerDep",
    "PokerlostTokenVerifierDep",
    "ServiceAccessTokenSignerDep",
    "SettingsDep",
    "authorize_pokerlost_request",
)
