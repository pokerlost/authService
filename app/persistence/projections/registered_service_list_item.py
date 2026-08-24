"""Registered-service list read projection."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from domain.types import ServiceId
from domain.value_model import ValueModel


class RegisteredServiceListItemProjection(ValueModel):
    """Safe registered-service summary without implementation metadata."""

    id: UUID
    service_id: ServiceId
    created_at: datetime
    updated_at: datetime
