"""Persisted human password credential."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from persistence.database.base import Base
from persistence.database.mixins import TimestampMixin

if TYPE_CHECKING:
    from .principal import Principal


class PasswordCredential(TimestampMixin, Base):
    """Argon2id password credential stored separately from account identity."""

    __tablename__ = "password_credentials"

    principal_id: Mapped[UUID] = mapped_column(
        ForeignKey("principals.id", ondelete="CASCADE"),
        primary_key=True,
    )
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    password_changed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    principal: Mapped[Principal] = relationship(
        back_populates="password_credential",
        lazy="raise",
    )
