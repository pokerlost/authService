"""Durable audit event page result."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from domain.value_model import ValueModel
from persistence.database.models import AuditEventModel


class AuditEventsPage(ValueModel):
    """One bounded audit page and optional exclusive next cursor."""

    items: list[AuditEventModel]
    next_before_occurred_at: datetime | None = None
    next_before_id: UUID | None = None
