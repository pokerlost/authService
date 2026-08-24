"""Human account enable orchestration."""

from __future__ import annotations

from application.errors import IntegrityError
from application.errors.accounts import HumanAccountNotFound
from application.time import UtcClock, utc_now
from domain.enums import AuditEventType, AuditResult, PrincipalStatus
from persistence.database.models import PrincipalModel
from persistence.repositories import SQLAlchemyAuditEventRepository, SQLAlchemyPrincipalRepository

from .command import EnableHumanAccountCommand


class EnableHumanAccountHandler:
    """Enable one human principal without restoring any revoked session state."""

    __slots__ = ("_audit_repository", "_clock", "_principal_repository")

    def __init__(
        self,
        *,
        principal_repository: SQLAlchemyPrincipalRepository,
        audit_repository: SQLAlchemyAuditEventRepository,
        clock: UtcClock = utc_now,
    ) -> None:
        self._principal_repository = principal_repository
        self._audit_repository = audit_repository
        self._clock = clock

    async def execute(self, command: EnableHumanAccountCommand) -> PrincipalModel:
        """Apply an idempotent active status transition inside the caller transaction."""
        principal = await self._principal_repository.get_by_id_for_update(
            command.target_principal_id,
        )
        if principal is None or not principal.role.is_human:
            raise HumanAccountNotFound
        if principal.status is not PrincipalStatus.ACTIVE:
            updated_principal = await self._principal_repository.set_status(
                principal_id=principal.id,
                status=PrincipalStatus.ACTIVE,
            )
            if updated_principal is None:
                raise IntegrityError
            principal = updated_principal
        context = command.audit_context
        await self._audit_repository.append(
            occurred_at=self._clock(),
            event_type=AuditEventType.ACCOUNT_ENABLED,
            result=AuditResult.SUCCESS,
            actor_principal_id=context.actor_principal_id,
            actor_role=context.actor_role,
            target_type="principal",
            target_id=str(principal.id),
            request_id=context.request_id,
            correlation_id=context.correlation_id,
            api_operation_id=context.api_operation_id,
            event_metadata={},
        )
        return principal
