"""Durable audit event list request."""

from __future__ import annotations

from datetime import datetime
from typing import Self
from uuid import UUID

from pydantic import Field, model_validator

from api.schemas.base import APIModel
from application.audit import ListAuditEventsQuery


class ListAuditEventsRequest(APIModel):
    """Bounded newest-first audit page with an optional composite keyset cursor."""

    limit: int = Field(default=50, ge=1, le=100)
    before_occurred_at: datetime | None = None
    before_id: UUID | None = None

    @model_validator(mode="after")
    def validate_cursor(self) -> Self:
        """Require both cursor components together or neither one."""
        if (self.before_occurred_at is None) != (self.before_id is None):
            raise ValueError("Audit cursor requires both occurredAt and id")
        return self

    def to_query(self) -> ListAuditEventsQuery:
        """Map transport pagination to the immutable read query."""
        return ListAuditEventsQuery(
            limit=self.limit,
            before_occurred_at=self.before_occurred_at,
            before_id=self.before_id,
        )
