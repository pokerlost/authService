"""Persisted source-service, audience, and OAuth2 scope grant."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import CheckConstraint, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from persistence.database import Base
from persistence.database.mixins import CreatedAtMixin


class ServiceScopeGrantModel(CreatedAtMixin, Base):
    """Grant one source service an exact operation scope for one target resource."""

    __tablename__ = "service_scope_grants"
    __table_args__ = (
        CheckConstraint(
            "char_length(audience) BETWEEN 2 AND 63",
            name="ck_service_scope_grants_audience_length",
        ),
        CheckConstraint(
            "audience = lower(audience) AND audience ~ '^[a-z0-9-]+$'",
            name="ck_service_scope_grants_audience_format",
        ),
    )

    service_principal_id: Mapped[UUID] = mapped_column(
        ForeignKey("service_principals.principal_id", ondelete="CASCADE"),
        primary_key=True,
    )
    audience: Mapped[str] = mapped_column(String(63), primary_key=True)
    api_operation_id: Mapped[str] = mapped_column(
        String(255),
        ForeignKey("operation_identities.api_operation_id", ondelete="RESTRICT"),
        primary_key=True,
    )
