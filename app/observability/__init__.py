"""Logfire observability facade."""

from __future__ import annotations

from .configure import configure_observability, instrument_application, instrument_database

__all__ = ("configure_observability", "instrument_application", "instrument_database")
