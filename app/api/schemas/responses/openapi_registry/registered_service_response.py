"""Registered service response schema."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from api.schemas.base import ResponseModel
from domain.types import ServiceId


class RegisteredServiceResponse(ResponseModel):
    """Platform service identity without implementation metadata."""

    id: UUID
    service_id: ServiceId
    created_at: datetime
    updated_at: datetime
