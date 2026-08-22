"""Shared API dependency facade."""

from __future__ import annotations

from .database import get_database_session
from .resources import get_application_resources
from .settings import get_settings

__all__ = ("get_application_resources", "get_database_session", "get_settings")
