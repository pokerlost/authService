"""Persisted human authentication session."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy.orm import Mapped, mapped_column

from domain.enums import SessionRevocationReason, SessionStatus
from persistence.database import UUIDModel
from persistence.database.mixins import TimestampMixin


class SessionModel(TimestampMixin, UUIDModel):
    """Server-tracked human session and refresh-token family."""

    __tablename__ = "sessions"
    __table_args__ = (
        CheckConstraint(
            "status IN ('active', 'revoked')",
            name="ck_sessions_status",
        ),
        CheckConstraint(
            "revocation_reason IS NULL OR revocation_reason IN "
            "('refresh_reuse', 'principal_disabled', 'invalid_human_role', "
            "'logout', 'logout_all', 'manual', 'password_changed', "
            "'password_reset', 'oauth2_migration')",
            name="ck_sessions_revocation_reason",
        ),
        CheckConstraint(
            "idle_expires_at <= absolute_expires_at",
            name="ck_sessions_expiration_order",
        ),
        CheckConstraint(
            "(status = 'active' AND revoked_at IS NULL AND revocation_reason IS NULL) OR "
            "(status = 'revoked' AND revoked_at IS NOT NULL AND revocation_reason IS NOT NULL)",
            name="ck_sessions_revocation_state",
        ),
        Index("ix_sessions_principal_id_status", "principal_id", "status"),
    )

    principal_id: Mapped[UUID] = mapped_column(
        ForeignKey("principals.id", ondelete="CASCADE"),
        nullable=False,
    )
    status: Mapped[SessionStatus] = mapped_column(
        SQLAlchemyEnum(
            SessionStatus,
            values_callable=lambda enum: [member.value for member in enum],
            native_enum=False,
            length=7,
            validate_strings=True,
        ),
        nullable=False,
    )
    last_refreshed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    idle_expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    absolute_expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    revocation_reason: Mapped[SessionRevocationReason | None] = mapped_column(
        SQLAlchemyEnum(
            SessionRevocationReason,
            values_callable=lambda enum: [member.value for member in enum],
            native_enum=False,
            length=24,
            validate_strings=True,
        ),
    )
