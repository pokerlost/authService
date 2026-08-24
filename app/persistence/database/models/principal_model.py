"""Persisted authentication principal."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, Index
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from domain.enums import PrincipalStatus, Role
from persistence.database import UUIDModel
from persistence.database.mixins import TimestampMixin

if TYPE_CHECKING:
    from .human_account_model import HumanAccountModel
    from .password_credential_model import PasswordCredentialModel
    from .service_principal_model import ServicePrincipalModel


class PrincipalModel(TimestampMixin, UUIDModel):
    """Human or machine authentication principal with one direct role."""

    __tablename__ = "principals"
    __table_args__ = (
        CheckConstraint(
            "role IN ('user', 'support', 'master', 'auto')",
            name="ck_principals_role",
        ),
        CheckConstraint(
            "status IN ('active', 'disabled')",
            name="ck_principals_status",
        ),
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
    human_account: Mapped[HumanAccountModel | None] = relationship(
        back_populates="principal",
        uselist=False,
        lazy="raise",
    )
    password_credential: Mapped[PasswordCredentialModel | None] = relationship(
        back_populates="principal",
        uselist=False,
        lazy="raise",
    )
    service_principal: Mapped[ServicePrincipalModel | None] = relationship(
        back_populates="principal",
        uselist=False,
        lazy="raise",
    )
