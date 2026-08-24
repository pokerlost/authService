"""Authenticated password change orchestration."""

from __future__ import annotations

from application.errors import CurrentPasswordInvalidError, IntegrityError
from application.security import Argon2PasswordHasher
from application.time import UtcClock, utc_now
from domain.enums import AuditEventType, AuditResult, SessionRevocationReason
from persistence.repositories import (
    SQLAlchemyAuditEventRepository,
    SQLAlchemyPasswordCredentialRepository,
    SQLAlchemyPrincipalRepository,
    SQLAlchemyRefreshTokenRepository,
    SQLAlchemySessionRepository,
)

from .command import ChangePasswordCommand


class ChangePasswordHandler:
    """Replace a verified password and revoke every human session atomically."""

    __slots__ = (
        "_audit_repository",
        "_clock",
        "_password_credential_repository",
        "_password_hasher",
        "_principal_repository",
        "_refresh_token_repository",
        "_session_repository",
    )

    def __init__(
        self,
        *,
        principal_repository: SQLAlchemyPrincipalRepository,
        password_credential_repository: SQLAlchemyPasswordCredentialRepository,
        session_repository: SQLAlchemySessionRepository,
        refresh_token_repository: SQLAlchemyRefreshTokenRepository,
        audit_repository: SQLAlchemyAuditEventRepository,
        password_hasher: Argon2PasswordHasher,
        clock: UtcClock = utc_now,
    ) -> None:
        self._principal_repository = principal_repository
        self._password_credential_repository = password_credential_repository
        self._session_repository = session_repository
        self._refresh_token_repository = refresh_token_repository
        self._audit_repository = audit_repository
        self._password_hasher = password_hasher
        self._clock = clock

    async def execute(self, command: ChangePasswordCommand) -> None:
        """Change the actor password and require a fresh password grant."""
        context = command.audit_context
        if context.actor_principal_id is None or context.actor_role is None:
            raise IntegrityError
        principal = await self._principal_repository.get_by_id_for_update(
            context.actor_principal_id
        )
        credential = await self._password_credential_repository.get_by_principal_id_for_update(
            context.actor_principal_id
        )
        if principal is None or not principal.role.is_human or credential is None:
            raise IntegrityError
        if not self._password_hasher.verify(
            command.current_password,
            credential.password_hash,
        ):
            raise CurrentPasswordInvalidError

        now = self._clock()
        updated = await self._password_credential_repository.replace_password(
            principal_id=principal.id,
            password_hash=self._password_hasher.hash(command.new_password),
            password_changed_at=now,
        )
        if updated is None:
            raise IntegrityError
        session_ids = await self._session_repository.revoke_all_active_for_principal(
            principal_id=principal.id,
            revoked_at=now,
            reason=SessionRevocationReason.PASSWORD_CHANGED,
        )
        await self._refresh_token_repository.revoke_active_for_sessions(
            session_ids=session_ids,
            revoked_at=now,
        )
        await self._audit_repository.append(
            occurred_at=now,
            event_type=AuditEventType.PASSWORD_CHANGED,
            result=AuditResult.SUCCESS,
            actor_principal_id=principal.id,
            actor_role=principal.role,
            target_type="principal",
            target_id=str(principal.id),
            request_id=context.request_id,
            correlation_id=context.correlation_id,
            api_operation_id=context.api_operation_id,
            event_metadata={"revokedSessionCount": len(session_ids)},
        )
