"""Persisted opaque refresh-token rotation state."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    LargeBinary,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from persistence.database import UUIDModel
from persistence.database.mixins import CreatedAtMixin


class RefreshTokenModel(CreatedAtMixin, UUIDModel):
    """Digest-only refresh credential in one session rotation chain."""

    __tablename__ = "refresh_tokens"
    __table_args__ = (
        CheckConstraint(
            "char_length(lookup_id) = 22 AND lookup_id ~ '^[A-Za-z0-9_-]+$'",
            name="ck_refresh_tokens_lookup_id",
        ),
        CheckConstraint(
            "octet_length(secret_digest) = 32",
            name="ck_refresh_tokens_secret_digest_length",
        ),
        CheckConstraint(
            "parent_token_id IS NULL OR parent_token_id <> id",
            name="ck_refresh_tokens_parent_not_self",
        ),
        CheckConstraint(
            "replaced_by_token_id IS NULL OR replaced_by_token_id <> id",
            name="ck_refresh_tokens_replacement_not_self",
        ),
        CheckConstraint(
            "(consumed_at IS NULL AND replaced_by_token_id IS NULL) OR "
            "(consumed_at IS NOT NULL AND replaced_by_token_id IS NOT NULL)",
            name="ck_refresh_tokens_consumption_link",
        ),
        CheckConstraint(
            "reuse_detected_at IS NULL OR consumed_at IS NOT NULL",
            name="ck_refresh_tokens_reuse_after_consumption",
        ),
        Index("ix_refresh_tokens_session_id", "session_id"),
        UniqueConstraint("lookup_id", name="uq_refresh_tokens_lookup_id"),
        UniqueConstraint("parent_token_id", name="uq_refresh_tokens_parent_token_id"),
        UniqueConstraint(
            "replaced_by_token_id",
            name="uq_refresh_tokens_replaced_by_token_id",
        ),
    )

    session_id: Mapped[UUID] = mapped_column(
        ForeignKey("sessions.id", ondelete="CASCADE"),
        nullable=False,
    )
    lookup_id: Mapped[str] = mapped_column(String(32), nullable=False)
    secret_digest: Mapped[bytes] = mapped_column(LargeBinary(32), nullable=False)
    parent_token_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("refresh_tokens.id"),
    )
    replaced_by_token_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("refresh_tokens.id"),
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    consumed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    reuse_detected_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
