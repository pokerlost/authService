"""PrincipalModel-isolated all-session logout orchestration."""

from __future__ import annotations

from application.time import UtcClock, utc_now
from domain.enums import AuditEventType, AuditResult, SessionRevocationReason
from persistence.repositories import (
    SQLAlchemyAuditEventRepository,
    SQLAlchemyRefreshTokenRepository,
    SQLAlchemySessionRepository,
)

from .command import RevokeAllSessionsCommand


class RevokeAllSessionsHandler:
    """Revoke every active session family owned by one authenticated principal."""

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

    async def execute(self, command: RevokeAllSessionsCommand) -> None:
        """Revoke active sessions and refresh rows with two set-based updates."""
        now = self._clock()
        session_ids = await self._session_repository.revoke_all_active_for_principal(
            principal_id=command.principal_id,
            revoked_at=now,
            reason=SessionRevocationReason.LOGOUT_ALL,
        )
        await self._refresh_token_repository.revoke_active_for_sessions(
            session_ids=session_ids,
            revoked_at=now,
        )
        context = command.audit_context
        await self._audit_repository.append(
            occurred_at=now,
            event_type=AuditEventType.ALL_SESSIONS_REVOKED,
            result=AuditResult.SUCCESS,
            actor_principal_id=context.actor_principal_id,
            actor_role=context.actor_role,
            target_type="principal",
            target_id=str(command.principal_id),
            request_id=context.request_id,
            correlation_id=context.correlation_id,
            api_operation_id=context.api_operation_id,
            event_metadata={"revokedSessionCount": len(session_ids)},
        )
