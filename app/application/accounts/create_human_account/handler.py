"""Trusted human account creation orchestration."""

from __future__ import annotations

from application.errors import InvalidOperationError
from application.errors.users import UsernameAlreadyRegistered
from application.security import Argon2PasswordHasher
from application.time import UtcClock, utc_now
from domain.enums import AuditEventType, AuditResult, PrincipalStatus, Role
from domain.types import canonicalize_username, normalize_nickname
from persistence.repositories import (
    SQLAlchemyAuditEventRepository,
    SQLAlchemyHumanAccountRepository,
    SQLAlchemyPasswordCredentialRepository,
    SQLAlchemyPrincipalRepository,
)

from .command import CreateHumanAccountCommand
from .result import CreatedHumanAccount


class CreateHumanAccountHandler:
    """Create one active human principal, identity, and password atomically."""

    __slots__ = (
        "_audit_repository",
        "_clock",
        "_human_account_repository",
        "_password_credential_repository",
        "_password_hasher",
        "_principal_repository",
    )

    def __init__(
        self,
        *,
        principal_repository: SQLAlchemyPrincipalRepository,
        human_account_repository: SQLAlchemyHumanAccountRepository,
        password_credential_repository: SQLAlchemyPasswordCredentialRepository,
        audit_repository: SQLAlchemyAuditEventRepository,
        password_hasher: Argon2PasswordHasher,
        clock: UtcClock = utc_now,
    ) -> None:
        self._principal_repository = principal_repository
        self._human_account_repository = human_account_repository
        self._password_credential_repository = password_credential_repository
        self._audit_repository = audit_repository
        self._password_hasher = password_hasher
        self._clock = clock

    async def execute(self, command: CreateHumanAccountCommand) -> CreatedHumanAccount:
        """Create only a user, support, or master identity in the caller transaction."""
        if not command.role.is_human:
            raise InvalidOperationError

        username = canonicalize_username(command.username)
        nickname = normalize_nickname(command.nickname)
        password_hash = self._password_hasher.hash(command.password)
        principal = await self._principal_repository.create(
            role=command.role,
            status=PrincipalStatus.ACTIVE,
        )
        human_account = await self._human_account_repository.create(
            principal_id=principal.id,
            username=username,
            nickname=nickname,
        )
        if human_account is None:
            raise UsernameAlreadyRegistered
        await self._password_credential_repository.create(
            principal_id=principal.id,
            password_hash=password_hash,
        )
        event_type = {
            Role.USER: AuditEventType.USER_REGISTERED,
            Role.SUPPORT: AuditEventType.SUPPORT_ACCOUNT_CREATED,
            Role.MASTER: AuditEventType.MASTER_ACCOUNT_CREATED,
        }[principal.role]
        context = command.audit_context
        await self._audit_repository.append(
            occurred_at=self._clock(),
            event_type=event_type,
            result=AuditResult.SUCCESS,
            actor_principal_id=context.actor_principal_id,
            actor_role=context.actor_role,
            target_type="principal",
            target_id=str(principal.id),
            request_id=context.request_id,
            correlation_id=context.correlation_id,
            api_operation_id=context.api_operation_id,
            event_metadata={"createdRole": principal.role.value},
        )
        return CreatedHumanAccount(
            id=principal.id,
            username=human_account.username,
            nickname=human_account.nickname,
            role=principal.role,
        )
