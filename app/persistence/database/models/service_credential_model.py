"""Persisted digest-only AUTO service credential."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, LargeBinary, String
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy.orm import Mapped, mapped_column

from domain.enums import ServiceCredentialStatus
from persistence.database import UUIDModel
from persistence.database.mixins import TimestampMixin


class ServiceCredentialModel(TimestampMixin, UUIDModel):
    """Finite rotatable service credential without plaintext secret material."""

    __tablename__ = "service_credentials"
    __table_args__ = (
        CheckConstraint(
            "char_length(client_id) BETWEEN 16 AND 64",
            name="ck_service_credentials_client_id_length",
        ),
        CheckConstraint(
            "client_id ~ '^[A-Za-z0-9_-]+$'",
            name="ck_service_credentials_client_id_format",
        ),
        CheckConstraint(
            "octet_length(secret_digest) = 32",
            name="ck_service_credentials_secret_digest_length",
        ),
        CheckConstraint(
            "status IN ('active', 'revoked')",
            name="ck_service_credentials_status",
        ),
        CheckConstraint(
            "expires_at > created_at",
            name="ck_service_credentials_expiration",
        ),
        CheckConstraint(
            "(status = 'active' AND revoked_at IS NULL) OR "
            "(status = 'revoked' AND revoked_at IS NOT NULL)",
            name="ck_service_credentials_revocation_state",
        ),
        Index("ix_service_credentials_service_principal_id", "service_principal_id"),
    )

    service_principal_id: Mapped[UUID] = mapped_column(
        ForeignKey("service_principals.principal_id", ondelete="CASCADE"),
        nullable=False,
    )
    client_id: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    secret_digest: Mapped[bytes] = mapped_column(LargeBinary(32), nullable=False)
    status: Mapped[ServiceCredentialStatus] = mapped_column(
        SQLAlchemyEnum(
            ServiceCredentialStatus,
            values_callable=lambda enum: [member.value for member in enum],
            native_enum=False,
            length=7,
            validate_strings=True,
        ),
        nullable=False,
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
