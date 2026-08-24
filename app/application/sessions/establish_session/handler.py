"""Human session establishment orchestration."""

from __future__ import annotations

from datetime import timedelta

from application.errors import InvalidOperationError
from application.security import AccessTokenIssuer, IssuedSessionTokens, RefreshTokenProtector
from application.time import UtcClock, utc_now
from domain.enums import PrincipalStatus, SessionStatus
from persistence.repositories import (
    SQLAlchemyPrincipalRepository,
    SQLAlchemyRefreshTokenRepository,
    SQLAlchemySessionRepository,
    SQLAlchemySessionScopeRepository,
)

from .command import EstablishSessionCommand


class EstablishSessionHandler:
    """Create one session family and its initial access and refresh credentials."""

    __slots__ = (
        "_absolute_ttl",
        "_access_token_issuer",
        "_clock",
        "_idle_ttl",
        "_principal_repository",
        "_refresh_token_protector",
        "_refresh_token_repository",
        "_refresh_token_ttl",
        "_session_repository",
        "_session_scope_repository",
    )

    def __init__(
        self,
        *,
        principal_repository: SQLAlchemyPrincipalRepository,
        session_repository: SQLAlchemySessionRepository,
        session_scope_repository: SQLAlchemySessionScopeRepository,
        refresh_token_repository: SQLAlchemyRefreshTokenRepository,
        refresh_token_protector: RefreshTokenProtector,
        access_token_issuer: AccessTokenIssuer,
        idle_ttl: timedelta,
        absolute_ttl: timedelta,
        refresh_token_ttl: timedelta,
        clock: UtcClock = utc_now,
    ) -> None:
        self._principal_repository = principal_repository
        self._session_repository = session_repository
        self._session_scope_repository = session_scope_repository
        self._refresh_token_repository = refresh_token_repository
        self._refresh_token_protector = refresh_token_protector
        self._access_token_issuer = access_token_issuer
        self._idle_ttl = idle_ttl
        self._absolute_ttl = absolute_ttl
        self._refresh_token_ttl = refresh_token_ttl
        self._clock = clock

    async def execute(self, command: EstablishSessionCommand) -> IssuedSessionTokens:
        """Establish a human session inside the caller-owned transaction."""
        principal = await self._principal_repository.get_by_id(command.principal_id)
        if (
            principal is None
            or principal.status is not PrincipalStatus.ACTIVE
            or not principal.role.is_human
        ):
            raise InvalidOperationError

        now = self._clock()
        absolute_expires_at = now + self._absolute_ttl
        session = await self._session_repository.create(
            principal_id=principal.id,
            status=SessionStatus.ACTIVE,
            last_refreshed_at=now,
            idle_expires_at=min(now + self._idle_ttl, absolute_expires_at),
            absolute_expires_at=absolute_expires_at,
        )
        await self._session_scope_repository.create_for_session(
            session_id=session.id,
            scopes=command.scopes,
        )
        issued_refresh_token = self._refresh_token_protector.generate()
        await self._refresh_token_repository.create(
            session_id=session.id,
            lookup_id=issued_refresh_token.lookup_id,
            secret_digest=issued_refresh_token.secret_digest,
            parent_token_id=None,
            expires_at=min(now + self._refresh_token_ttl, absolute_expires_at),
        )
        access_token = self._access_token_issuer.issue_human_access_token(
            principal.id,
            session.id,
            principal.role,
            command.scopes,
        )
        return IssuedSessionTokens(
            access_token=access_token,
            refresh_token=issued_refresh_token.token,
            scopes=command.scopes,
        )
