"""Ordinary-user registration orchestration."""

from __future__ import annotations

from application.errors.users import EmailAlreadyRegistered
from application.security import Argon2PasswordHasher
from domain.enums import PrincipalStatus, Role
from persistence.database.models import Principal
from persistence.repositories import (
    SQLAlchemyHumanAccountRepository,
    SQLAlchemyPasswordCredentialRepository,
    SQLAlchemyPrincipalRepository,
)

from .command import RegisterUserCommand


class RegisterUserHandler:
    """Create one active ordinary-user principal and credential atomically."""

    __slots__ = (
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
        password_hasher: Argon2PasswordHasher,
    ) -> None:
        self._principal_repository = principal_repository
        self._human_account_repository = human_account_repository
        self._password_credential_repository = password_credential_repository
        self._password_hasher = password_hasher

    async def execute(self, command: RegisterUserCommand) -> Principal:
        """Register an ordinary user inside the caller-owned transaction."""
        email = str(command.email)
        normalized_email = email.casefold()
        password_hash = self._password_hasher.hash(command.password)
        principal = await self._principal_repository.create(
            role=Role.USER,
            status=PrincipalStatus.ACTIVE,
        )
        human_account = await self._human_account_repository.create(
            principal_id=principal.id,
            email=email,
            normalized_email=normalized_email,
        )
        if human_account is None:
            raise EmailAlreadyRegistered
        await self._password_credential_repository.create(
            principal_id=principal.id,
            password_hash=password_hash,
        )
        return principal
