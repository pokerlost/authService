"""ORM creation and update timestamp mixin."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from .created_at import CreatedAtMixin


class TimestampMixin(CreatedAtMixin):
    """Add a SQLAlchemy-managed UTC update timestamp."""

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
