"""Persisted authorization scope catalog SQLAlchemy model."""

from __future__ import annotations

from sqlalchemy import CheckConstraint, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from persistence.database import UUIDModel
from persistence.database.mixins import TimestampMixin


class ScopeDefinitionModel(TimestampMixin, UUIDModel):
    """Persist one exact authorization scope definition."""

    __tablename__ = "scope_definitions"
    __table_args__ = (
        CheckConstraint(
            "name ~ '^[a-z][A-Za-z0-9]*([.][a-z][A-Za-z0-9]*)+$'",
            name="ck_scope_definitions_name_format",
        ),
        CheckConstraint(
            "length(btrim(description)) > 0",
            name="ck_scope_definitions_description_not_empty",
        ),
        UniqueConstraint("name", name="uq_scope_definitions_name"),
    )

    name: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
