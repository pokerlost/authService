"""Persisted human authentication account."""

from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import CheckConstraint, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from persistence.database import Base
from persistence.database.mixins import TimestampMixin

if TYPE_CHECKING:
    from .principal_model import PrincipalModel


class HumanAccountModel(TimestampMixin, Base):
    """Canonical login username and non-unique display nickname for a human principal."""

    __tablename__ = "human_accounts"
    __table_args__ = (
        CheckConstraint(
            "username = lower(username)",
            name="ck_human_accounts_username_lowercase",
        ),
        CheckConstraint(
            "char_length(username) BETWEEN 3 AND 32",
            name="ck_human_accounts_username_length",
        ),
        CheckConstraint(
            "username ~ '^[a-z0-9_]+$'",
            name="ck_human_accounts_username_format",
        ),
        CheckConstraint(
            "nickname = btrim(nickname) AND char_length(nickname) BETWEEN 1 AND 64",
            name="ck_human_accounts_nickname",
        ),
        UniqueConstraint("username", name="uq_human_accounts_username"),
    )

    principal_id: Mapped[UUID] = mapped_column(
        ForeignKey("principals.id", ondelete="CASCADE"),
        primary_key=True,
    )
    username: Mapped[str] = mapped_column(String(32), nullable=False)
    nickname: Mapped[str] = mapped_column(String(64), nullable=False)
    principal: Mapped[PrincipalModel] = relationship(
        back_populates="human_account",
        lazy="raise",
    )
