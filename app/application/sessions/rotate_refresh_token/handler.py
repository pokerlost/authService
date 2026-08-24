"""Serialized opaque refresh-token rotation orchestration."""

from __future__ import annotations

from datetime import datetime, timedelta

from application.errors import IntegrityError
from application.security import (
    AccessTokenIssuer,
    IssuedSessionTokens,
    OAuthScopeParser,
    RefreshTokenProtector,
)
from application.time import UtcClock, utc_now
from domain.enums import (
    PrincipalStatus,
    RefreshRotationStatus,
    SessionRevocationReason,
    SessionStatus,
)
from persistence.database.models import RefreshTokenModel, SessionModel
from persistence.queries import SQLAlchemyScopeQuery
from persistence.repositories import (
    SQLAlchemyPrincipalRepository,
    SQLAlchemyRefreshTokenRepository,
    SQLAlchemySessionRepository,
    SQLAlchemySessionScopeRepository,
)

from .command import RotateRefreshTokenCommand
from .result import RefreshRotationResult


class RotateRefreshTokenHandler:
    """Rotate one refresh token with strict reuse detection and family revocation."""

    __slots__ = (
        "_access_token_issuer",
        "_clock",
        "_idle_ttl",
        "_principal_repository",
        "_refresh_token_protector",
        "_refresh_token_repository",
        "_refresh_token_ttl",
        "_scope_parser",
        "_scope_query",
        "_session_repository",
        "_session_scope_repository",
    )

    def __init__(
        self,
        *,
        principal_repository: SQLAlchemyPrincipalRepository,
        session_repository: SQLAlchemySessionRepository,
        refresh_token_repository: SQLAlchemyRefreshTokenRepository,
        session_scope_repository: SQLAlchemySessionScopeRepository,
        scope_query: SQLAlchemyScopeQuery,
        scope_parser: OAuthScopeParser,
        refresh_token_protector: RefreshTokenProtector,
        access_token_issuer: AccessTokenIssuer,
        idle_ttl: timedelta,
        refresh_token_ttl: timedelta,
        clock: UtcClock = utc_now,
    ) -> None:
        self._principal_repository = principal_repository
        self._session_repository = session_repository
        self._refresh_token_repository = refresh_token_repository
        self._session_scope_repository = session_scope_repository
        self._scope_query = scope_query
        self._scope_parser = scope_parser
        self._refresh_token_protector = refresh_token_protector
        self._access_token_issuer = access_token_issuer
        self._idle_ttl = idle_ttl
        self._refresh_token_ttl = refresh_token_ttl
        self._clock = clock

    async def execute(self, command: RotateRefreshTokenCommand) -> RefreshRotationResult:
        """Return an outcome so security mutations can commit without exception rollback."""
        parsed_token = self._refresh_token_protector.parse(command.refresh_token)
        if parsed_token is None:
            return RefreshRotationResult(status=RefreshRotationStatus.INVALID)

        refresh_token = await self._refresh_token_repository.get_by_lookup_id_for_update(
            parsed_token.lookup_id,
        )
        if refresh_token is None or not self._refresh_token_protector.verify_digest(
            parsed_token,
            refresh_token.secret_digest,
        ):
            return RefreshRotationResult(status=RefreshRotationStatus.INVALID)

        session = await self._session_repository.get_by_id_for_update(refresh_token.session_id)
        if session is None:
            raise IntegrityError

        now = self._clock()
        if refresh_token.consumed_at is not None:
            return await self._handle_reuse(
                refresh_token=refresh_token,
                session=session,
                detected_at=now,
            )
        if refresh_token.revoked_at is not None or session.status is SessionStatus.REVOKED:
            return RefreshRotationResult(status=RefreshRotationStatus.REVOKED)
        if (
            now >= refresh_token.expires_at
            or now >= session.idle_expires_at
            or now >= session.absolute_expires_at
        ):
            return RefreshRotationResult(status=RefreshRotationStatus.EXPIRED)

        principal = await self._principal_repository.get_by_id(session.principal_id)
        if principal is None:
            raise IntegrityError
        if principal.status is not PrincipalStatus.ACTIVE:
            await self._revoke_family(
                session=session,
                revoked_at=now,
                reason=SessionRevocationReason.PRINCIPAL_DISABLED,
            )
            return RefreshRotationResult(status=RefreshRotationStatus.REVOKED)
        if not principal.role.is_human:
            await self._revoke_family(
                session=session,
                revoked_at=now,
                reason=SessionRevocationReason.INVALID_HUMAN_ROLE,
            )
            return RefreshRotationResult(status=RefreshRotationStatus.REVOKED)

        original_scope_rows = await self._session_scope_repository.list_for_session(session.id)
        original_scopes = frozenset(row.api_operation_id for row in original_scope_rows)
        active_grants = await self._scope_query.list_active_for_role(principal.role)
        currently_granted_scopes = frozenset(grant.api_operation_id for grant in active_grants)
        current_ceiling = original_scopes & currently_granted_scopes
        try:
            requested_scopes = self._scope_parser.parse_requested(command.requested_scope)
        except ValueError:
            return RefreshRotationResult(status=RefreshRotationStatus.INVALID_SCOPE)
        if command.requested_scope is None or not command.requested_scope.strip():
            scopes = current_ceiling
        elif not requested_scopes.issubset(original_scopes) or not requested_scopes.issubset(
            currently_granted_scopes
        ):
            return RefreshRotationResult(status=RefreshRotationStatus.INVALID_SCOPE)
        else:
            scopes = requested_scopes

        issued_refresh_token = self._refresh_token_protector.generate()
        replacement = await self._refresh_token_repository.create(
            session_id=session.id,
            lookup_id=issued_refresh_token.lookup_id,
            secret_digest=issued_refresh_token.secret_digest,
            parent_token_id=refresh_token.id,
            expires_at=min(now + self._refresh_token_ttl, session.absolute_expires_at),
        )
        consumed = await self._refresh_token_repository.mark_consumed_and_replaced(
            token_id=refresh_token.id,
            consumed_at=now,
            replaced_by_token_id=replacement.id,
        )
        if consumed is None:
            raise IntegrityError
        updated_session = await self._session_repository.update_after_refresh(
            session_id=session.id,
            last_refreshed_at=now,
            idle_expires_at=min(now + self._idle_ttl, session.absolute_expires_at),
        )
        if updated_session is None:
            raise IntegrityError

        access_token = self._access_token_issuer.issue_human_access_token(
            principal.id,
            session.id,
            principal.role,
            scopes,
        )
        return RefreshRotationResult(
            status=RefreshRotationStatus.SUCCESS,
            tokens=IssuedSessionTokens(
                access_token=access_token,
                refresh_token=issued_refresh_token.token,
                scopes=scopes,
            ),
            principal_id=principal.id,
            session_id=session.id,
            role=principal.role,
        )

    async def _handle_reuse(
        self,
        *,
        refresh_token: RefreshTokenModel,
        session: SessionModel,
        detected_at: datetime,
    ) -> RefreshRotationResult:
        reused = await self._refresh_token_repository.mark_reuse_detected(
            token_id=refresh_token.id,
            detected_at=detected_at,
        )
        if reused is None:
            raise IntegrityError
        await self._revoke_family(
            session=session,
            revoked_at=detected_at,
            reason=SessionRevocationReason.REFRESH_REUSE,
        )
        principal = await self._principal_repository.get_by_id(session.principal_id)
        return RefreshRotationResult(
            status=RefreshRotationStatus.REUSE_DETECTED,
            principal_id=session.principal_id,
            session_id=session.id,
            role=principal.role if principal is not None else None,
        )

    async def _revoke_family(
        self,
        *,
        session: SessionModel,
        revoked_at: datetime,
        reason: SessionRevocationReason,
    ) -> None:
        await self._session_repository.revoke(
            session_id=session.id,
            revoked_at=revoked_at,
            reason=reason,
        )
        await self._refresh_token_repository.revoke_active_for_session(
            session_id=session.id,
            revoked_at=revoked_at,
        )
