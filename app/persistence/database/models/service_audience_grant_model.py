"""Direct service-principal audience grant SQLAlchemy model."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import CheckConstraint, ForeignKeyConstraint, Text
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column

from persistence.database import Base
from persistence.database.mixins import CreatedAtMixin


class ServiceAudienceGrantModel(CreatedAtMixin, Base):
    """Persist one exact resource URI granted to a service principal."""

    __tablename__ = "service_audience_grants"
    __table_args__ = (
        CheckConstraint(
            "audience ~ '^urn:pokerlost:service:[a-z][A-Za-z0-9]*$'",
            name="ck_service_audience_grants_audience_format",
        ),
        ForeignKeyConstraint(
            ("principal_id",),
            ("authorization_principals.id",),
            name="fk_service_audience_grants_principal_authorization_principals",
            ondelete="RESTRICT",
        ),
    )

    principal_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        primary_key=True,
    )
    audience: Mapped[str] = mapped_column(Text, primary_key=True)
