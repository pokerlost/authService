"""Declarative SQLAlchemy metadata root."""

from __future__ import annotations

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base for authService ORM mappings and Alembic metadata."""
