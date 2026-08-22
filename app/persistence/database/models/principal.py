"""Persisted authentication principal."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, Index
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from domain.enums import PrincipalStatus, Role
from persistence.database.mixins import TimestampMixin, UUIDModel

if TYPE_CHECKING:
    from .human_account import HumanAccount
    from .password_credential import PasswordCredential


class Principal(TimestampMixin, UUIDModel):
    """Human or machine authentication principal with one direct role."""

    __tablename__ = "principals"
    __table_args__ = (
        CheckConstraint("role IN ('user', 'support', 'master', 'auto')", name="role"),
        CheckConstraint("status IN ('active', 'disabled')", name="status"),
        Index("ix_principals_role_status", "role", "status"),
    )

    role: Mapped[Role] = mapped_column(
        SQLAlchemyEnum(
            Role,
            values_callable=lambda enum: [member.value for member in enum],
            native_enum=False,
            length=7,
            validate_strings=True,
        ),
        nullable=False,
    )
    status: Mapped[PrincipalStatus] = mapped_column(
        SQLAlchemyEnum(
            PrincipalStatus,
            values_callable=lambda enum: [member.value for member in enum],
            native_enum=False,
            length=8,
            validate_strings=True,
        ),
        nullable=False,
    )
    human_account: Mapped[HumanAccount | None] = relationship(
        back_populates="principal",
        uselist=False,
        lazy="raise",
    )
    password_credential: Mapped[PasswordCredential | None] = relationship(
        back_populates="principal",
        uselist=False,
        lazy="raise",
    )
