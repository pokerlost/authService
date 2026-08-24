"""Independent transaction boundary for durable failed-operation audit."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from application.time import UtcClock, utc_now
from domain.enums import AuditEventType, AuditResult, Role
from persistence.repositories import SQLAlchemyAuditEventRepository

from .context import AuditContext


class DurableAuditFailureRecorder:
    """Commit a failure event independently when the business transaction must roll back."""

    __slots__ = ("_clock", "_session_factory")

    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        *,
        clock: UtcClock = utc_now,
    ) -> None:
        self._session_factory = session_factory
        self._clock = clock

    async def append(
        self,
        *,
        event_type: AuditEventType,
        context: AuditContext,
        reason: str,
        target_type: str | None = None,
        target_id: str | UUID | None = None,
        actor_principal_id: UUID | None = None,
        actor_role: Role | None = None,
    ) -> None:
        """Append and commit one sanitized failure event in a dedicated transaction."""
        async with self._session_factory.begin() as session:
            await SQLAlchemyAuditEventRepository(session).append(
                occurred_at=self._clock(),
                event_type=event_type,
                result=AuditResult.FAILURE,
                actor_principal_id=actor_principal_id or context.actor_principal_id,
                actor_role=actor_role or context.actor_role,
                target_type=target_type,
                target_id=str(target_id) if target_id is not None else None,
                request_id=context.request_id,
                correlation_id=context.correlation_id,
                api_operation_id=context.api_operation_id,
                event_metadata={"reason": reason},
            )
