"""OAuth2 client secret credential SQLAlchemy model."""

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


class OAuthClientSecretModel(TimestampMixin, UUIDModel):
    """Persist one digest-only OAuth2 confidential-client credential."""

    __tablename__ = "oauth_client_secrets"
    __table_args__ = (
        CheckConstraint(
            "octet_length(secret_digest) = 32",
            name="ck_oauth_client_secrets_secret_digest_length",
        ),
        CheckConstraint(
            "status IN ('active', 'retiring', 'revoked')",
            name="ck_oauth_client_secrets_status",
        ),
        CheckConstraint(
            "updated_at >= created_at",
            name="ck_oauth_client_secrets_updated_at",
        ),
        CheckConstraint(
            "expires_at IS NULL OR expires_at > created_at",
            name="ck_oauth_client_secrets_expires_at",
        ),
        CheckConstraint(
            "revoked_at IS NULL OR revoked_at >= created_at",
            name="ck_oauth_client_secrets_revoked_at",
        ),
        CheckConstraint(
            "(status IN ('active', 'retiring') AND revoked_at IS NULL) OR "
            "(status = 'revoked' AND revoked_at IS NOT NULL)",
            name="ck_oauth_client_secrets_state",
        ),
        ForeignKeyConstraint(
            ("client_id",),
            ("oauth_clients.id",),
            name="fk_oauth_client_secrets_client_id_oauth_clients",
            ondelete="RESTRICT",
        ),
        UniqueConstraint(
            "secret_digest",
            name="uq_oauth_client_secrets_secret_digest",
        ),
        Index("ix_oauth_client_secrets_client_id", "client_id"),
    )

    client_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        nullable=False,
    )
    secret_digest: Mapped[bytes] = mapped_column(
        LargeBinary,
        nullable=False,
    )
    status: Mapped[str] = mapped_column(String(16), nullable=False)
    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    revoked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
