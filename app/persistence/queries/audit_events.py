"""Bounded keyset query for durable security audit events."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import and_, or_, select

from persistence.database.models import AuditEventModel
from persistence.repositories.base import SQLAlchemyRepository


class SQLAlchemyAuditEventQuery(SQLAlchemyRepository):
    """Read immutable audit events in stable newest-first keyset order."""

    async def list_page(
        self,
        *,
        limit: int,
        before_occurred_at: datetime | None,
        before_id: UUID | None,
    ) -> list[AuditEventModel]:
        """Return at most one bounded page without OFFSET."""
        statement = select(AuditEventModel).order_by(
            AuditEventModel.occurred_at.desc(),
            AuditEventModel.id.desc(),
        )
        if before_occurred_at is not None and before_id is not None:
            statement = statement.where(
                or_(
                    AuditEventModel.occurred_at < before_occurred_at,
                    and_(
                        AuditEventModel.occurred_at == before_occurred_at,
                        AuditEventModel.id < before_id,
                    ),
                )
            )
        result = await self._read_scalar(statement.limit(limit))
        return result.all()
