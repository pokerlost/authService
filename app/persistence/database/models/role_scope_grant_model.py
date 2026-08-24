"""Persisted explicit human role-to-operation scope grant."""

from __future__ import annotations

from sqlalchemy import CheckConstraint, ForeignKey, String
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy.orm import Mapped, mapped_column

from domain.enums import Role
from persistence.database import Base
from persistence.database.mixins import CreatedAtMixin


class RoleScopeGrantModel(CreatedAtMixin, Base):
    """Grant one exact canonical operation scope to one direct human role."""

    __tablename__ = "role_scope_grants"
    __table_args__ = (
        CheckConstraint(
            "role IN ('user', 'support', 'master')",
            name="ck_role_scope_grants_human_role",
        ),
    )

    role: Mapped[Role] = mapped_column(
        SQLAlchemyEnum(
            Role,
            values_callable=lambda enum: [member.value for member in enum],
            native_enum=False,
            length=7,
            validate_strings=True,
        ),
        primary_key=True,
    )
    api_operation_id: Mapped[str] = mapped_column(
        String(255),
        ForeignKey("operation_identities.api_operation_id", ondelete="RESTRICT"),
        primary_key=True,
    )
