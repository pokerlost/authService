"""OAuth2 client aggregate SQLAlchemy model."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import CheckConstraint, ForeignKeyConstraint, String
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column

from persistence.database import UUIDModel
from persistence.database.mixins import TimestampMixin


class OAuthClientModel(TimestampMixin, UUIDModel):
    """Persist one public or confidential OAuth2 client."""

    __tablename__ = "oauth_clients"
    __table_args__ = (
        CheckConstraint(
            "client_type IN ('public', 'confidential')",
            name="ck_oauth_clients_client_type",
        ),
        CheckConstraint(
            "status IN ('active', 'disabled')",
            name="ck_oauth_clients_status",
        ),
        CheckConstraint(
            "(client_type = 'public' AND bound_principal_id IS NULL) OR "
            "(client_type = 'confidential' AND bound_principal_id IS NOT NULL)",
            name="ck_oauth_clients_binding",
        ),
        ForeignKeyConstraint(
            ("bound_principal_id",),
            ("authorization_principals.id",),
            name="fk_oauth_clients_bound_principal_id_authorization_principals",
            ondelete="RESTRICT",
        ),
    )

    client_type: Mapped[str] = mapped_column(String(16), nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False)
    bound_principal_id: Mapped[UUID | None] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        nullable=True,
    )
