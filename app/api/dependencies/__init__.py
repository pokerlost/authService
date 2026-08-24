"""Shared API dependency facade."""

from __future__ import annotations

from .database import DatabaseSession, get_database_session
from .resources import ApplicationResourcesDep, get_application_resources
from .settings import SettingsDep, get_settings

__all__ = (
    "ApplicationResourcesDep",
    "DatabaseSession",
    "SettingsDep",
    "get_application_resources",
    "get_database_session",
    "get_settings",
)
