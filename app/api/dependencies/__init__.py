"""Shared API dependency alias facade."""

from __future__ import annotations

from .database import DatabaseSession
from .resources import ApplicationResourcesDep, BusinessOperationFingerprinterDep
from .settings import SettingsDep

__all__ = (
    "ApplicationResourcesDep",
    "BusinessOperationFingerprinterDep",
    "DatabaseSession",
    "SettingsDep",
)
