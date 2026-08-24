"""Persisted AUTO service identity."""

from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import CheckConstraint, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from persistence.database import Base
from persistence.database.mixins import TimestampMixin

if TYPE_CHECKING:
    from .principal_model import PrincipalModel


class ServicePrincipalModel(TimestampMixin, Base):
    """Canonical backend-service identity attached only to an AUTO principal."""

    __tablename__ = "service_principals"
    __table_args__ = (
        CheckConstraint(
            "char_length(service_slug) BETWEEN 2 AND 63",
            name="ck_service_principals_service_slug_length",
        ),
        CheckConstraint(
            "service_slug = lower(service_slug)",
            name="ck_service_principals_service_slug_lowercase",
        ),
        CheckConstraint(
            "service_slug ~ '^[a-z0-9-]+$'",
            name="ck_service_principals_service_slug_format",
        ),
        UniqueConstraint("service_slug", name="uq_service_principals_service_slug"),
    )

    principal_id: Mapped[UUID] = mapped_column(
        ForeignKey("principals.id", ondelete="CASCADE"),
        primary_key=True,
    )
    service_slug: Mapped[str] = mapped_column(String(63), nullable=False)
    principal: Mapped[PrincipalModel] = relationship(
        back_populates="service_principal",
        lazy="raise",
    )
