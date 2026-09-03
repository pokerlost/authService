"""Authorization-client credential SQLAlchemy model."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKeyConstraint,
    Index,
    LargeBinary,
    String,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column

from persistence.database import UUIDModel
from persistence.database.mixins import TimestampMixin


class ClientCredentialModel(TimestampMixin, UUIDModel):
    """Persist one digest-only confidential-client credential."""

    __tablename__ = "client_credentials"
    __table_args__ = (
        CheckConstraint(
            "octet_length(secret_digest) = 32",
            name="ck_client_credentials_secret_digest_length",
        ),
        CheckConstraint(
            "status IN ('active', 'retiring', 'revoked')",
            name="ck_client_credentials_status",
        ),
        CheckConstraint(
            "updated_at >= created_at",
            name="ck_client_credentials_updated_at",
        ),
        CheckConstraint(
            "expires_at IS NULL OR expires_at > created_at",
            name="ck_client_credentials_expires_at",
        ),
        CheckConstraint(
            "revoked_at IS NULL OR revoked_at >= created_at",
            name="ck_client_credentials_revoked_at",
        ),
        CheckConstraint(
            "(status IN ('active', 'retiring') AND revoked_at IS NULL) OR "
            "(status = 'revoked' AND revoked_at IS NOT NULL)",
            name="ck_client_credentials_state",
        ),
        ForeignKeyConstraint(
            ("client_id",),
            ("oauth_clients.id",),
            name="fk_client_credentials_client_id_oauth_clients",
            ondelete="RESTRICT",
        ),
        UniqueConstraint("secret_digest", name="uq_client_credentials_secret_digest"),
        Index("ix_client_credentials_client_id", "client_id"),
    )

    client_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        nullable=False,
    )
    secret_digest: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
