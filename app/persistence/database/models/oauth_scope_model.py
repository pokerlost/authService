"""Persisted OAuth2 scope catalog SQLAlchemy model."""

from __future__ import annotations

from sqlalchemy import CheckConstraint, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from persistence.database import UUIDModel
from persistence.database.mixins import TimestampMixin


class OAuthScopeModel(TimestampMixin, UUIDModel):
    """Persist one exact OAuth2 scope catalog entry."""

    __tablename__ = "oauth_scopes"
    __table_args__ = (
        CheckConstraint(
            "name ~ '^[a-z][a-z0-9_]*([.][a-z][a-z0-9_]*)+$'",
            name="ck_oauth_scopes_name_format",
        ),
        CheckConstraint(
            "length(btrim(description)) > 0",
            name="ck_oauth_scopes_description_not_empty",
        ),
        UniqueConstraint("name", name="uq_oauth_scopes_name"),
    )

    name: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
