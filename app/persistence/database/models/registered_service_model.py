"""Persisted PokerLost OpenAPI registry service identity."""

from __future__ import annotations

from sqlalchemy import CheckConstraint, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from persistence.database import UUIDModel
from persistence.database.mixins import TimestampMixin


class RegisteredServiceModel(TimestampMixin, UUIDModel):
    """Case-sensitive platform service identity extracted from contract metadata."""

    __tablename__ = "registered_services"
    __table_args__ = (
        CheckConstraint(
            "char_length(service_id) BETWEEN 2 AND 63",
            name="ck_registered_services_service_id_length",
        ),
        CheckConstraint(
            "service_id ~ '^[a-z][A-Za-z0-9]{1,62}$'",
            name="ck_registered_services_service_id_format",
        ),
        UniqueConstraint("service_id", name="uq_registered_services_service_id"),
    )

    service_id: Mapped[str] = mapped_column(String(63), nullable=False)
