"""Unified password, refresh-token, and client-credentials grant orchestration."""

from __future__ import annotations

from uuid import UUID

from pydantic import ValidationError

from application.authentication import LoginCommand, LoginHandler
from application.errors import (
    InvalidCredentials,
    InvalidOAuthScope,
    InvalidServiceCredentials,
)
from application.fingerprinting import canonical_fingerprint
from application.security import SecurityRateLimiter, SecurityRateLimitPolicy
from application.service_authentication import IssueServiceTokenCommand, IssueServiceTokenHandler
from application.sessions import RotateRefreshTokenCommand, RotateRefreshTokenHandler
from application.time import UtcClock, utc_now
from domain.enums import (
    AuditEventType,
    AuditResult,
    OAuthTokenStatus,
    RateLimitKind,
    RefreshRotationStatus,
    Role,
)
from persistence.repositories import SQLAlchemyAuditEventRepository

from .command import OAuthTokenCommand
from .result import OAuthTokenResult


class OAuthTokenHandler:
    """Issue every PokerLost access token through one transactional OAuth2 operation."""

    __slots__ = (
        "_audit_repository",
        "_client_credentials_handler",
        "_client_credentials_policy",
        "_clock",
        "_human_access_token_ttl_seconds",
        "_login_handler",
        "_machine_access_token_ttl_seconds",
        "_password_policy",
        "_rate_limiter",
        "_refresh_handler",
    )

    def __init__(
        self,
        *,
        login_handler: LoginHandler,
        refresh_handler: RotateRefreshTokenHandler,
        client_credentials_handler: IssueServiceTokenHandler,
        audit_repository: SQLAlchemyAuditEventRepository,
        rate_limiter: SecurityRateLimiter,
        password_policy: SecurityRateLimitPolicy,
        client_credentials_policy: SecurityRateLimitPolicy,
        human_access_token_ttl_seconds: int,
        machine_access_token_ttl_seconds: int,
        clock: UtcClock = utc_now,
    ) -> None:
        self._login_handler = login_handler
        self._refresh_handler = refresh_handler
        self._client_credentials_handler = client_credentials_handler
        self._audit_repository = audit_repository
        self._rate_limiter = rate_limiter
        self._password_policy = password_policy
        self._client_credentials_policy = client_credentials_policy
        self._human_access_token_ttl_seconds = human_access_token_ttl_seconds
        self._machine_access_token_ttl_seconds = machine_access_token_ttl_seconds
        self._clock = clock

    async def execute(self, command: OAuthTokenCommand) -> OAuthTokenResult:
        """Dispatch one supported grant while preserving durable failure state."""
        if command.grant_type == "password":
            return await self._password_grant(command)
        if command.grant_type == "refresh_token":
            return await self._refresh_grant(command)
        if command.grant_type == "client_credentials":
            return await self._client_credentials_grant(command)
        return OAuthTokenResult(status=OAuthTokenStatus.UNSUPPORTED_GRANT_TYPE)

    async def _password_grant(self, command: OAuthTokenCommand) -> OAuthTokenResult:
        username = command.username or ""
        key_fingerprint = canonical_fingerprint(
            {"kind": "password", "username": username.strip().lower()}
        )
        now = self._clock()
        if await self._rate_limiter.is_limited(
            kind=RateLimitKind.PASSWORD,
            key_fingerprint=key_fingerprint,
            now=now,
        ):
            await self._audit_failure(
                command,
                event_type=AuditEventType.PASSWORD_GRANT_FAILED,
                reason="rate_limited",
            )
            return OAuthTokenResult(status=OAuthTokenStatus.RATE_LIMITED)

        if command.username is None or command.password is None:
            return await self._failed_password_auth(command, key_fingerprint, "invalid_grant")
        try:
            result = await self._login_handler.execute(
                LoginCommand(
                    username=command.username,
                    password=command.password,
                    requested_scope=command.scope,
                )
            )
        except (InvalidCredentials, ValidationError):
            return await self._failed_password_auth(command, key_fingerprint, "invalid_grant")
        except InvalidOAuthScope:
            await self._rate_limiter.clear(
                kind=RateLimitKind.PASSWORD,
                key_fingerprint=key_fingerprint,
            )
            await self._audit_failure(
                command,
                event_type=AuditEventType.PASSWORD_GRANT_FAILED,
                reason="invalid_scope",
            )
            return OAuthTokenResult(status=OAuthTokenStatus.INVALID_SCOPE)

        await self._rate_limiter.clear(
            kind=RateLimitKind.PASSWORD,
            key_fingerprint=key_fingerprint,
        )
        await self._append_audit(
            command,
            event_type=AuditEventType.PASSWORD_GRANT_SUCCEEDED,
            result=AuditResult.SUCCESS,
            actor_principal_id=result.principal_id,
            actor_role=result.role,
            target_type="principal",
            target_id=str(result.principal_id),
            event_metadata={"scopeCount": len(result.scopes)},
        )
        return OAuthTokenResult(
            status=OAuthTokenStatus.SUCCESS,
            access_token=result.access_token,
            refresh_token=result.refresh_token,
            expires_in=self._human_access_token_ttl_seconds,
            scopes=result.scopes,
        )

    async def _failed_password_auth(
        self,
        command: OAuthTokenCommand,
        key_fingerprint: str,
        reason: str,
    ) -> OAuthTokenResult:
        limited = await self._rate_limiter.record_failure(
            kind=RateLimitKind.PASSWORD,
            key_fingerprint=key_fingerprint,
            policy=self._password_policy,
            now=self._clock(),
        )
        await self._audit_failure(
            command,
            event_type=AuditEventType.PASSWORD_GRANT_FAILED,
            reason="rate_limited" if limited else reason,
        )
        return OAuthTokenResult(
            status=OAuthTokenStatus.RATE_LIMITED if limited else OAuthTokenStatus.INVALID_GRANT
        )

    async def _refresh_grant(self, command: OAuthTokenCommand) -> OAuthTokenResult:
        if command.refresh_token is None:
            return OAuthTokenResult(status=OAuthTokenStatus.INVALID_GRANT)
        result = await self._refresh_handler.execute(
            RotateRefreshTokenCommand(
                refresh_token=command.refresh_token,
                requested_scope=command.scope,
            )
        )
        if result.status is RefreshRotationStatus.INVALID_SCOPE:
            return OAuthTokenResult(status=OAuthTokenStatus.INVALID_SCOPE)
        if result.status is RefreshRotationStatus.REUSE_DETECTED:
            await self._append_audit(
                command,
                event_type=AuditEventType.OAUTH_REFRESH_REUSE_DETECTED,
                result=AuditResult.FAILURE,
                actor_principal_id=result.principal_id,
                actor_role=result.role,
                target_type="session",
                target_id=str(result.session_id) if result.session_id is not None else None,
                event_metadata={"reason": "refresh_reuse"},
            )
            return OAuthTokenResult(status=OAuthTokenStatus.INVALID_GRANT)
        if result.status is not RefreshRotationStatus.SUCCESS or result.tokens is None:
            return OAuthTokenResult(status=OAuthTokenStatus.INVALID_GRANT)
        await self._append_audit(
            command,
            event_type=AuditEventType.OAUTH_TOKEN_REFRESHED,
            result=AuditResult.SUCCESS,
            actor_principal_id=result.principal_id,
            actor_role=result.role,
            target_type="session",
            target_id=str(result.session_id) if result.session_id is not None else None,
            event_metadata={"scopeCount": len(result.tokens.scopes)},
        )
        return OAuthTokenResult(
            status=OAuthTokenStatus.SUCCESS,
            access_token=result.tokens.access_token,
            refresh_token=result.tokens.refresh_token,
            expires_in=self._human_access_token_ttl_seconds,
            scopes=result.tokens.scopes,
        )

    async def _client_credentials_grant(self, command: OAuthTokenCommand) -> OAuthTokenResult:
        client_id = command.client_id or ""
        key_fingerprint = canonical_fingerprint(
            {"clientId": client_id, "kind": "client_credentials"}
        )
        now = self._clock()
        if await self._rate_limiter.is_limited(
            kind=RateLimitKind.CLIENT_CREDENTIALS,
            key_fingerprint=key_fingerprint,
            now=now,
        ):
            await self._audit_failure(
                command,
                event_type=AuditEventType.CLIENT_CREDENTIALS_FAILED,
                reason="rate_limited",
            )
            return OAuthTokenResult(status=OAuthTokenStatus.RATE_LIMITED)
        if command.client_id is None or command.client_secret is None or command.resource is None:
            return await self._failed_client_auth(command, key_fingerprint, "invalid_client")
        try:
            result = await self._client_credentials_handler.execute(
                IssueServiceTokenCommand(
                    client_id=command.client_id,
                    client_secret=command.client_secret,
                    audience=command.resource,
                    requested_scope=command.scope,
                )
            )
        except (InvalidServiceCredentials, ValidationError):
            return await self._failed_client_auth(command, key_fingerprint, "invalid_client")
        except InvalidOAuthScope:
            await self._rate_limiter.clear(
                kind=RateLimitKind.CLIENT_CREDENTIALS,
                key_fingerprint=key_fingerprint,
            )
            await self._audit_failure(
                command,
                event_type=AuditEventType.CLIENT_CREDENTIALS_FAILED,
                reason="invalid_scope",
            )
            return OAuthTokenResult(status=OAuthTokenStatus.INVALID_SCOPE)

        await self._rate_limiter.clear(
            kind=RateLimitKind.CLIENT_CREDENTIALS,
            key_fingerprint=key_fingerprint,
        )
        await self._append_audit(
            command,
            event_type=AuditEventType.CLIENT_CREDENTIALS_SUCCEEDED,
            result=AuditResult.SUCCESS,
            actor_principal_id=result.principal_id,
            actor_role=Role.AUTO,
            target_type="resource",
            target_id=command.resource,
            event_metadata={"scopeCount": len(result.scopes)},
        )
        return OAuthTokenResult(
            status=OAuthTokenStatus.SUCCESS,
            access_token=result.access_token,
            expires_in=self._machine_access_token_ttl_seconds,
            scopes=result.scopes,
        )

    async def _failed_client_auth(
        self,
        command: OAuthTokenCommand,
        key_fingerprint: str,
        reason: str,
    ) -> OAuthTokenResult:
        limited = await self._rate_limiter.record_failure(
            kind=RateLimitKind.CLIENT_CREDENTIALS,
            key_fingerprint=key_fingerprint,
            policy=self._client_credentials_policy,
            now=self._clock(),
        )
        await self._audit_failure(
            command,
            event_type=AuditEventType.CLIENT_CREDENTIALS_FAILED,
            reason="rate_limited" if limited else reason,
        )
        return OAuthTokenResult(
            status=OAuthTokenStatus.RATE_LIMITED if limited else OAuthTokenStatus.INVALID_CLIENT
        )

    async def _audit_failure(
        self,
        command: OAuthTokenCommand,
        *,
        event_type: AuditEventType,
        reason: str,
    ) -> None:
        await self._append_audit(
            command,
            event_type=event_type,
            result=AuditResult.FAILURE,
            event_metadata={"reason": reason},
        )

    async def _append_audit(
        self,
        command: OAuthTokenCommand,
        *,
        event_type: AuditEventType,
        result: AuditResult,
        actor_principal_id: UUID | None = None,
        actor_role: Role | None = None,
        target_type: str | None = None,
        target_id: str | None = None,
        event_metadata: dict[str, object] | None = None,
    ) -> None:
        context = command.audit_context
        await self._audit_repository.append(
            occurred_at=self._clock(),
            event_type=event_type,
            result=result,
            actor_principal_id=actor_principal_id,
            actor_role=actor_role,
            target_type=target_type,
            target_id=target_id,
            request_id=context.request_id,
            correlation_id=context.correlation_id,
            api_operation_id=context.api_operation_id,
            event_metadata=event_metadata,
        )
