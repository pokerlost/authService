"""Durable security audit event responses."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from api.schemas.base import ResponseModel
from domain.enums import AuditEventType, AuditResult, Role


class AuditEventResponse(ResponseModel):
    """One immutable safe security audit event."""

    id: UUID
    occurred_at: datetime
    event_type: AuditEventType
    result: AuditResult
    actor_principal_id: UUID | None
    actor_role: Role | None
    target_type: str | None
    target_id: str | None
    request_id: str | None
    correlation_id: str | None
    api_operation_id: str | None
    metadata: dict[str, object]


class AuditEventsPageResponse(ResponseModel):
    """Bounded newest-first audit page and optional continuation cursor."""

    items: list[AuditEventResponse]
    next_before_occurred_at: datetime | None = None
    next_before_id: UUID | None = None
