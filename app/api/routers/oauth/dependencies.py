"""Unified OAuth2 token operation dependency composition."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends, Form, Security
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from api.dependencies import ApplicationResourcesDep, DatabaseSession, SettingsDep
from api.schemas.requests import OAuthTokenRequest
from application.authentication import LoginHandler
from application.oauth import OAuthTokenHandler
from application.security import SecurityRateLimiter, SecurityRateLimitPolicy
from application.service_authentication import IssueServiceTokenHandler
from application.sessions import EstablishSessionHandler, RotateRefreshTokenHandler
from persistence.queries import SQLAlchemyScopeQuery
from persistence.repositories import (
    SQLAlchemyAuditEventRepository,
    SQLAlchemyHumanAccountRepository,
    SQLAlchemyPasswordCredentialRepository,
    SQLAlchemyPrincipalRepository,
    SQLAlchemyRefreshTokenRepository,
    SQLAlchemySecurityRateLimitRepository,
    SQLAlchemyServiceAudienceGrantRepository,
    SQLAlchemyServiceCredentialRepository,
    SQLAlchemyServicePrincipalRepository,
    SQLAlchemySessionRepository,
    SQLAlchemySessionScopeRepository,
)

oauth_client_authentication = HTTPBasic(
    auto_error=False,
    scheme_name="OAuth2ClientAuthentication",
    description="HTTP Basic client authentication for the client_credentials grant.",
)

type OAuthTokenFormDep = Annotated[OAuthTokenRequest, Form()]
type OAuthClientAuthenticationDep = Annotated[
    HTTPBasicCredentials | None,
    Security(oauth_client_authentication),
]


def provide_oauth_token_handler(
    session: DatabaseSession,
    resources: ApplicationResourcesDep,
    settings: SettingsDep,
) -> OAuthTokenHandler:
    """Compose all OAuth2 grants with one request transaction and shared security state."""
    principal_repository = SQLAlchemyPrincipalRepository(session)
    session_repository = SQLAlchemySessionRepository(session)
    refresh_token_repository = SQLAlchemyRefreshTokenRepository(session)
    session_scope_repository = SQLAlchemySessionScopeRepository(session)
    scope_query = SQLAlchemyScopeQuery(session)
    establish_session_handler = EstablishSessionHandler(
        principal_repository=principal_repository,
        session_repository=session_repository,
        session_scope_repository=session_scope_repository,
        refresh_token_repository=refresh_token_repository,
        refresh_token_protector=resources.refresh_token_protector,
        access_token_issuer=resources.access_token_issuer,
        idle_ttl=settings.session.idle_ttl,
        absolute_ttl=settings.session.absolute_ttl,
        refresh_token_ttl=settings.refresh_token.ttl,
    )
    login_handler = LoginHandler(
        principal_repository=principal_repository,
        human_account_repository=SQLAlchemyHumanAccountRepository(session),
        password_credential_repository=SQLAlchemyPasswordCredentialRepository(session),
        password_hasher=resources.password_hasher,
        establish_session_handler=establish_session_handler,
        scope_query=scope_query,
        scope_parser=resources.oauth_scope_parser,
    )
    refresh_handler = RotateRefreshTokenHandler(
        principal_repository=principal_repository,
        session_repository=session_repository,
        refresh_token_repository=refresh_token_repository,
        session_scope_repository=session_scope_repository,
        scope_query=scope_query,
        scope_parser=resources.oauth_scope_parser,
        refresh_token_protector=resources.refresh_token_protector,
        access_token_issuer=resources.access_token_issuer,
        idle_ttl=settings.session.idle_ttl,
        refresh_token_ttl=settings.refresh_token.ttl,
    )
    client_credentials_handler = IssueServiceTokenHandler(
        principal_repository=principal_repository,
        service_principal_repository=SQLAlchemyServicePrincipalRepository(session),
        service_credential_repository=SQLAlchemyServiceCredentialRepository(session),
        grant_repository=SQLAlchemyServiceAudienceGrantRepository(session),
        protector=resources.service_credential_protector,
        issuer=resources.machine_access_token_issuer,
        scope_query=scope_query,
        scope_parser=resources.oauth_scope_parser,
    )
    return OAuthTokenHandler(
        login_handler=login_handler,
        refresh_handler=refresh_handler,
        client_credentials_handler=client_credentials_handler,
        audit_repository=SQLAlchemyAuditEventRepository(session),
        rate_limiter=SecurityRateLimiter(SQLAlchemySecurityRateLimitRepository(session)),
        password_policy=SecurityRateLimitPolicy(
            max_attempts=settings.rate_limit.password_attempts,
            window=settings.rate_limit.password_window,
            lock=settings.rate_limit.password_lock,
        ),
        client_credentials_policy=SecurityRateLimitPolicy(
            max_attempts=settings.rate_limit.service_credential_attempts,
            window=settings.rate_limit.service_credential_window,
            lock=settings.rate_limit.service_credential_lock,
        ),
        human_access_token_ttl_seconds=settings.jwt.access_token_ttl_seconds,
        machine_access_token_ttl_seconds=settings.service_auth.access_token_ttl_seconds,
    )


type OAuthTokenHandlerDep = Annotated[
    OAuthTokenHandler,
    Depends(provide_oauth_token_handler),
]
