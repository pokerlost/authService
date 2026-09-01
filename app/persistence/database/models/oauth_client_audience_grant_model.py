"""Direct OAuth2 client audience grant SQLAlchemy model."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import CheckConstraint, ForeignKeyConstraint, Text
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column

from persistence.database import Base
from persistence.database.mixins import CreatedAtMixin


class OAuthClientAudienceGrantModel(CreatedAtMixin, Base):
    """Persist one exact resource URI granted to an OAuth2 client."""

    __tablename__ = "oauth_client_audience_grants"
    __table_args__ = (
        CheckConstraint(
            "audience ~ '^urn:pokerlost:service:[a-z][A-Za-z0-9]*$'",
            name="ck_oauth_client_audience_grants_audience_format",
        ),
        ForeignKeyConstraint(
            ("client_id",),
            ("oauth_clients.id",),
            name="fk_oauth_client_audience_grants_client_id_oauth_clients",
            ondelete="RESTRICT",
        ),
    )

    client_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        primary_key=True,
    )
    audience: Mapped[str] = mapped_column(Text, primary_key=True)
