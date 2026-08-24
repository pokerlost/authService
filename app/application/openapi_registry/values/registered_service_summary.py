"""Registered PokerLost service summary."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from domain.types import ServiceId
from domain.value_model import ValueModel


class RegisteredServiceSummary(ValueModel):
    """Control-plane service identity without implementation metadata."""

    id: UUID
    service_id: ServiceId
    created_at: datetime
    updated_at: datetime
