"""Durable audit event keyset query."""

from __future__ import annotations

from datetime import datetime
from typing import Self
from uuid import UUID

from pydantic import Field, model_validator

from domain.value_model import ValueModel


class ListAuditEventsQuery(ValueModel):
    """Bounded newest-first audit page request with a composite cursor."""

    limit: int = Field(default=50, ge=1, le=100)
    before_occurred_at: datetime | None = None
    before_id: UUID | None = None

    @model_validator(mode="after")
    def validate_cursor(self) -> Self:
        """Require both keyset fields together or neither field."""
        if (self.before_occurred_at is None) != (self.before_id is None):
            raise ValueError("Audit cursor requires both occurred_at and id")
        return self
