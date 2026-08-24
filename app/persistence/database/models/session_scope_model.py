"""Persisted original OAuth2 scope ceiling for a human session."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from persistence.database import Base
from persistence.database.mixins import CreatedAtMixin


class SessionScopeModel(CreatedAtMixin, Base):
    """Remember one originally granted canonical operation scope for a session."""

    __tablename__ = "session_scopes"

    session_id: Mapped[UUID] = mapped_column(
        ForeignKey("sessions.id", ondelete="CASCADE"),
        primary_key=True,
    )
    api_operation_id: Mapped[str] = mapped_column(
        String(255),
        ForeignKey("operation_identities.api_operation_id", ondelete="RESTRICT"),
        primary_key=True,
    )
