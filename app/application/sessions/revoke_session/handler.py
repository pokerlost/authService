"""Owned-session manual revocation orchestration."""

from __future__ import annotations

from application.errors import SessionNotFound
from application.time import UtcClock, utc_now
from domain.enums import AuditEventType, AuditResult, SessionRevocationReason
from persistence.repositories import (
    SQLAlchemyAuditEventRepository,
    SQLAlchemyRefreshTokenRepository,
    SQLAlchemySessionRepository,
)

from .command import RevokeSessionCommand


class RevokeSessionHandler:
    """Revoke one owned session without revealing foreign session existence."""

    __slots__ = (
        "_audit_repository",
        "_clock",
        "_refresh_token_repository",
        "_session_repository",
    )

    def __init__(
        self,
        *,
        session_repository: SQLAlchemySessionRepository,
        refresh_token_repository: SQLAlchemyRefreshTokenRepository,
        audit_repository: SQLAlchemyAuditEventRepository,
        clock: UtcClock = utc_now,
    ) -> None:
        self._session_repository = session_repository
        self._refresh_token_repository = refresh_token_repository
        self._audit_repository = audit_repository
        self._clock = clock

    async def execute(self, command: RevokeSessionCommand) -> None:
        """Lock, ownership-check, and revoke one session family."""
        session = await self._session_repository.get_by_id_for_update(command.session_id)
        if session is None or session.principal_id != command.principal_id:
            raise SessionNotFound

        now = self._clock()
        await self._session_repository.revoke(
            session_id=session.id,
            revoked_at=now,
            reason=SessionRevocationReason.MANUAL,
        )
        await self._refresh_token_repository.revoke_active_for_session(
            session_id=session.id,
            revoked_at=now,
        )
        context = command.audit_context
        await self._audit_repository.append(
            occurred_at=now,
            event_type=AuditEventType.SESSION_REVOKED,
            result=AuditResult.SUCCESS,
            actor_principal_id=context.actor_principal_id,
            actor_role=context.actor_role,
            target_type="session",
            target_id=str(session.id),
            request_id=context.request_id,
            correlation_id=context.correlation_id,
            api_operation_id=context.api_operation_id,
            event_metadata={"reason": SessionRevocationReason.MANUAL.value},
        )
