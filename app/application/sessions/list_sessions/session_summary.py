"""Safe application session summary."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from domain.enums import SessionStatus
from domain.value_model import ValueModel


class SessionSummary(ValueModel):
    """Safe persisted session state plus current-session marker."""

    id: UUID
    status: SessionStatus
    created_at: datetime
    last_refreshed_at: datetime
    idle_expires_at: datetime
    absolute_expires_at: datetime
    revoked_at: datetime | None
    current: bool
