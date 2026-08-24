"""PostgreSQL-backed authentication rate-limit state."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, Index, Integer, String
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy.orm import Mapped, mapped_column

from domain.enums import RateLimitKind
from persistence.database import Base
from persistence.database.mixins import TimestampMixin


class SecurityRateLimitModel(TimestampMixin, Base):
    """Atomic per-fingerprint attempt window and temporary lock state."""

    __tablename__ = "security_rate_limits"
    __table_args__ = (
        CheckConstraint(
            "kind IN ('password', 'client_credentials')",
            name="ck_security_rate_limits_kind",
        ),
        CheckConstraint(
            "key_fingerprint ~ '^[0-9a-f]{64}$'",
            name="ck_security_rate_limits_key_fingerprint",
        ),
        CheckConstraint(
            "attempt_count >= 0",
            name="ck_security_rate_limits_attempt_count",
        ),
        Index("ix_security_rate_limits_updated_at", "updated_at"),
    )

    kind: Mapped[RateLimitKind] = mapped_column(
        SQLAlchemyEnum(
            RateLimitKind,
            values_callable=lambda enum: [member.value for member in enum],
            native_enum=False,
            length=18,
            validate_strings=True,
        ),
        primary_key=True,
    )
    key_fingerprint: Mapped[str] = mapped_column(String(64), primary_key=True)
    window_started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    attempt_count: Mapped[int] = mapped_column(Integer, nullable=False)
    locked_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
