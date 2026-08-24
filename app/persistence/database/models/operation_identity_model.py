"""Permanent global semantic operation ownership claim."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column

from persistence.database import Base


class OperationIdentityModel(Base):
    """Bind one API operation ID permanently to one registered service."""

    __tablename__ = "operation_identities"
    __table_args__ = (
        CheckConstraint(
            "char_length(api_operation_id) BETWEEN 3 AND 255",
            name="ck_operation_identities_api_operation_id_length",
        ),
        CheckConstraint(
            "api_operation_id ~ '^[a-z][A-Za-z0-9]{1,62}(\\.[a-z][A-Za-z0-9]{0,62}){1,2}$'",
            name="ck_operation_identities_api_operation_id_format",
        ),
    )

    api_operation_id: Mapped[str] = mapped_column(String(255), primary_key=True)
    registered_service_id: Mapped[UUID] = mapped_column(
        ForeignKey("registered_services.id", ondelete="RESTRICT"),
        nullable=False,
    )
    claimed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
