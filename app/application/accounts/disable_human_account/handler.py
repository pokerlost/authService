"""Human account disable orchestration."""

from __future__ import annotations

from application.errors import IntegrityError
from application.errors.accounts import CurrentAccountDisableForbidden, HumanAccountNotFound
from application.time import UtcClock, utc_now
from domain.enums import (
    AuditEventType,
    AuditResult,
    PrincipalStatus,
    SessionRevocationReason,
)
from persistence.database.models import PrincipalModel
from persistence.repositories import (
    SQLAlchemyAuditEventRepository,
    SQLAlchemyPrincipalRepository,
    SQLAlchemyRefreshTokenRepository,
    SQLAlchemySessionRepository,
)

from .command import DisableHumanAccountCommand


class DisableHumanAccountHandler:
    """Disable one human principal and revoke all of its active session families."""

    __slots__ = (
        "_audit_repository",
        "_clock",
        "_principal_repository",
        "_refresh_token_repository",
        "_session_repository",
    )

    def __init__(
        self,
        *,
        principal_repository: SQLAlchemyPrincipalRepository,
        session_repository: SQLAlchemySessionRepository,
        refresh_token_repository: SQLAlchemyRefreshTokenRepository,
        audit_repository: SQLAlchemyAuditEventRepository,
        clock: UtcClock = utc_now,
    ) -> None:
        self._principal_repository = principal_repository
        self._session_repository = session_repository
        self._refresh_token_repository = refresh_token_repository
        self._audit_repository = audit_repository
        self._clock = clock

    async def execute(self, command: DisableHumanAccountCommand) -> PrincipalModel:
        """Apply an idempotent disable and revoke active session credentials atomically."""
        principal = await self._principal_repository.get_by_id_for_update(
            command.target_principal_id,
        )
        if principal is None or not principal.role.is_human:
            raise HumanAccountNotFound
        context = command.audit_context
        if principal.id == context.actor_principal_id:
            raise CurrentAccountDisableForbidden

        if principal.status is not PrincipalStatus.DISABLED:
            updated_principal = await self._principal_repository.set_status(
                principal_id=principal.id,
                status=PrincipalStatus.DISABLED,
            )
            if updated_principal is None:
                raise IntegrityError
            principal = updated_principal

        now = self._clock()
        session_ids = await self._session_repository.revoke_all_active_for_principal(
            principal_id=principal.id,
            revoked_at=now,
            reason=SessionRevocationReason.PRINCIPAL_DISABLED,
        )
        await self._refresh_token_repository.revoke_active_for_sessions(
            session_ids=session_ids,
            revoked_at=now,
        )
        await self._audit_repository.append(
            occurred_at=now,
            event_type=AuditEventType.ACCOUNT_DISABLED,
            result=AuditResult.SUCCESS,
            actor_principal_id=context.actor_principal_id,
            actor_role=context.actor_role,
            target_type="principal",
            target_id=str(principal.id),
            request_id=context.request_id,
            correlation_id=context.correlation_id,
            api_operation_id=context.api_operation_id,
            event_metadata={"revokedSessionCount": len(session_ids)},
        )
        return principal
