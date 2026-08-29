"""Persisted authorization role SQLAlchemy model."""

from __future__ import annotations

from sqlalchemy import CheckConstraint, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from persistence.database import UUIDModel
from persistence.database.mixins import TimestampMixin


class AuthorizationRoleModel(TimestampMixin, UUIDModel):
    """Persist one closed role and its compatible principal category."""

    __tablename__ = "authorization_roles"
    __table_args__ = (
        CheckConstraint(
            "code IN ('user', 'support', 'master', 'auto')",
            name="ck_authorization_roles_code",
        ),
        CheckConstraint(
            "principal_type IN ('human', 'service')",
            name="ck_authorization_roles_principal_type",
        ),
        CheckConstraint(
            "(principal_type = 'human' AND code IN ('user', 'support', 'master')) "
            "OR (principal_type = 'service' AND code = 'auto')",
            name="ck_authorization_roles_code_principal_type",
        ),
        UniqueConstraint("code", name="uq_authorization_roles_code"),
        UniqueConstraint(
            "id",
            "principal_type",
            name="uq_authorization_roles_id_principal_type",
        ),
    )

    code: Mapped[str] = mapped_column(String(16), nullable=False)
    principal_type: Mapped[str] = mapped_column(String(16), nullable=False)
