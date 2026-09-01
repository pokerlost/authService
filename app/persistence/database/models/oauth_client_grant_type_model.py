"""Explicit OAuth2 client grant-type SQLAlchemy model."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import CheckConstraint, ForeignKeyConstraint, String
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column

from persistence.database import Base
from persistence.database.mixins import CreatedAtMixin


class OAuthClientGrantTypeModel(CreatedAtMixin, Base):
    """Persist one explicitly permitted OAuth2 grant type for a client."""

    __tablename__ = "oauth_client_grant_types"
    __table_args__ = (
        CheckConstraint(
            "grant_type IN ('client_credentials', 'refresh_token', "
            "'urn:pokerlost:params:oauth:grant-type:login-grant')",
            name="ck_oauth_client_grant_types_grant_type",
        ),
        ForeignKeyConstraint(
            ("client_id",),
            ("oauth_clients.id",),
            name="fk_oauth_client_grant_types_client_id_oauth_clients",
            ondelete="RESTRICT",
        ),
    )

    client_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        primary_key=True,
    )
    grant_type: Mapped[str] = mapped_column(
        String(64),
        primary_key=True,
    )
