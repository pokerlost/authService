"""Persisted human authentication account."""

from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from persistence.database.base import Base
from persistence.database.mixins import CreatedAtMixin

if TYPE_CHECKING:
    from .principal import Principal


class HumanAccount(CreatedAtMixin, Base):
    """Human principal email identity with normalized unique lookup."""

    __tablename__ = "human_accounts"
    __table_args__ = (
        UniqueConstraint("normalized_email", name="uq_human_accounts_normalized_email"),
    )

    principal_id: Mapped[UUID] = mapped_column(
        ForeignKey("principals.id", ondelete="CASCADE"),
        primary_key=True,
    )
    email: Mapped[str] = mapped_column(String(320), nullable=False)
    normalized_email: Mapped[str] = mapped_column(String(320), nullable=False)
    principal: Mapped[Principal] = relationship(
        back_populates="human_account",
        lazy="raise",
    )
