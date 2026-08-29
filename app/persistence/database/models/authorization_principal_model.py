"""Authorization principal aggregate SQLAlchemy model."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import CheckConstraint, ForeignKeyConstraint, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column

from persistence.database import UUIDModel
from persistence.database.mixins import TimestampMixin


class AuthorizationPrincipalModel(TimestampMixin, UUIDModel):
    """Persist one human or service authorization principal."""

    __tablename__ = "authorization_principals"
    __table_args__ = (
        CheckConstraint(
            "principal_type IN ('human', 'service')",
            name="ck_authorization_principals_principal_type",
        ),
        CheckConstraint(
            "status IN ('active', 'disabled')",
            name="ck_authorization_principals_status",
        ),
        CheckConstraint(
            "(principal_type = 'human' AND account_id IS NOT NULL "
            "AND service_slug IS NULL) OR "
            "(principal_type = 'service' AND account_id IS NULL "
            "AND service_slug IS NOT NULL)",
            name="ck_authorization_principals_binding",
        ),
        CheckConstraint(
            "service_slug IS NULL OR length(btrim(service_slug)) > 0",
            name="ck_authorization_principals_service_slug_not_empty",
        ),
        UniqueConstraint(
            "account_id",
            name="uq_authorization_principals_account_id",
        ),
        UniqueConstraint(
            "service_slug",
            name="uq_authorization_principals_service_slug",
        ),
        ForeignKeyConstraint(
            ("role_id", "principal_type"),
            ("authorization_roles.id", "authorization_roles.principal_type"),
            name="fk_authorization_principals_role_id_authorization_roles",
            ondelete="RESTRICT",
        ),
    )

    principal_type: Mapped[str] = mapped_column(String(16), nullable=False)
    role_id: Mapped[UUID] = mapped_column(PostgreSQLUUID(as_uuid=True), nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False)
    account_id: Mapped[UUID | None] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        nullable=True,
    )
    service_slug: Mapped[str | None] = mapped_column(Text, nullable=True)
