"""Human login orchestration."""

from __future__ import annotations

from application.errors import IntegrityError, InvalidCredentials, InvalidOAuthScope
from application.security import Argon2PasswordHasher, OAuthScopeParser
from application.sessions import EstablishSessionCommand, EstablishSessionHandler
from domain.enums import PrincipalStatus
from domain.types import canonicalize_username
from persistence.queries import SQLAlchemyScopeQuery
from persistence.repositories import (
    SQLAlchemyHumanAccountRepository,
    SQLAlchemyPasswordCredentialRepository,
    SQLAlchemyPrincipalRepository,
)

from .command import LoginCommand
from .result import LoginResult


class LoginHandler:
    """Verify one human credential and establish a new server-tracked session."""

    __slots__ = (
        "_establish_session_handler",
        "_human_account_repository",
        "_password_credential_repository",
        "_password_hasher",
        "_principal_repository",
        "_scope_parser",
        "_scope_query",
    )

    def __init__(
        self,
        *,
        principal_repository: SQLAlchemyPrincipalRepository,
        human_account_repository: SQLAlchemyHumanAccountRepository,
        password_credential_repository: SQLAlchemyPasswordCredentialRepository,
        password_hasher: Argon2PasswordHasher,
        establish_session_handler: EstablishSessionHandler,
        scope_query: SQLAlchemyScopeQuery,
        scope_parser: OAuthScopeParser,
    ) -> None:
        self._principal_repository = principal_repository
        self._human_account_repository = human_account_repository
        self._password_credential_repository = password_credential_repository
        self._password_hasher = password_hasher
        self._establish_session_handler = establish_session_handler
        self._scope_query = scope_query
        self._scope_parser = scope_parser

    async def execute(self, command: LoginCommand) -> LoginResult:
        """Authenticate a human without exposing credential failure distinctions."""
        username = canonicalize_username(command.username)
        human_account = await self._human_account_repository.get_by_username(username)
        if human_account is None:
            self._password_hasher.verify_or_dummy(command.password, None)
            raise InvalidCredentials

        password_credential = await self._password_credential_repository.get_by_principal_id(
            human_account.principal_id,
        )
        if password_credential is None:
            raise IntegrityError

        password_valid = self._password_hasher.verify_or_dummy(
            command.password,
            password_credential.password_hash,
        )
        if not password_valid:
            raise InvalidCredentials

        principal = await self._principal_repository.get_by_id_for_update(
            human_account.principal_id,
        )
        if principal is None:
            raise IntegrityError
        if not principal.role.is_human:
            raise IntegrityError
        if principal.status is not PrincipalStatus.ACTIVE:
            raise InvalidCredentials

        if self._password_hasher.needs_rehash(password_credential.password_hash):
            replacement = await self._password_credential_repository.replace_hash_for_rehash(
                principal_id=principal.id,
                password_hash=self._password_hasher.hash(command.password),
            )
            if replacement is None:
                raise IntegrityError

        active_grants = await self._scope_query.list_active_for_role(principal.role)
        allowed_scopes = frozenset(grant.api_operation_id for grant in active_grants)
        try:
            requested_scopes = self._scope_parser.parse_requested(command.requested_scope)
        except ValueError:
            raise InvalidOAuthScope from None
        if command.requested_scope is None or not command.requested_scope.strip():
            scopes = allowed_scopes
        elif not requested_scopes.issubset(allowed_scopes):
            raise InvalidOAuthScope
        else:
            scopes = requested_scopes
        tokens = await self._establish_session_handler.execute(
            EstablishSessionCommand(principal_id=principal.id, scopes=scopes),
        )
        return LoginResult(
            principal_id=principal.id,
            role=principal.role,
            access_token=tokens.access_token,
            refresh_token=tokens.refresh_token,
            scopes=tokens.scopes,
        )
