"""Canonical OAuth2 scope authentication for authService-owned human RPCs."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends, Request, Security
from fastapi.openapi.models import OAuthFlowClientCredentials, OAuthFlowPassword, OAuthFlows
from fastapi.security import OAuth2, SecurityScopes
from pydantic import SecretStr

from application.authentication import AuthenticatedHumanPrincipal
from application.errors import InsufficientScopeError, InvalidAccessToken
from application.security import AccessTokenVerifier
from application.time import utc_now
from domain.authservice_scopes import AUTH_SERVICE_PROTECTED_SCOPE_IDS
from domain.enums import PrincipalStatus, SessionStatus
from persistence.repositories import SQLAlchemyPrincipalRepository, SQLAlchemySessionRepository

from .database import DatabaseSession
from .resources import ApplicationResourcesDep

_SCOPE_DESCRIPTIONS = {
    scope: f"Invoke the {scope} PokerLost RPC operation."
    for scope in sorted(AUTH_SERVICE_PROTECTED_SCOPE_IDS)
}


class OAuth2Bearer(OAuth2):
    """Extract one Bearer token while publishing the complete PokerLost OAuth2 profile."""

    async def __call__(self, request: Request) -> str | None:
        """Return only a well-formed Bearer credential without raising framework errors."""
        authorization = request.headers.get("Authorization")
        if authorization is None:
            return None
        scheme, separator, credential = authorization.partition(" ")
        if separator != " " or scheme.lower() != "bearer" or not credential:
            return None
        return credential


oauth2_scheme = OAuth2Bearer(
    flows=OAuthFlows(
        password=OAuthFlowPassword(
            tokenUrl="/oauth.token",
            refreshUrl="/oauth.token",
            scopes=_SCOPE_DESCRIPTIONS,
        ),
        clientCredentials=OAuthFlowClientCredentials(
            tokenUrl="/oauth.token",
            scopes=_SCOPE_DESCRIPTIONS,
        ),
    ),
    scheme_name="OAuth2",
    description="PokerLost OAuth2 access JWT with canonical operationId scopes.",
    auto_error=False,
)

type OAuth2AccessTokenDep = Annotated[str | None, Security(oauth2_scheme)]


def get_access_token_verifier(resources: ApplicationResourcesDep) -> AccessTokenVerifier:
    """Return the lifespan-owned access-token verifier."""
    return resources.access_token_verifier


type AccessTokenVerifierDep = Annotated[
    AccessTokenVerifier,
    Depends(get_access_token_verifier),
]


async def authenticate_human_principal(
    security_scopes: SecurityScopes,
    access_token: OAuth2AccessTokenDep,
    verifier: AccessTokenVerifierDep,
    session: DatabaseSession,
) -> AuthenticatedHumanPrincipal:
    """Verify Bearer claims against current local session and principal state."""
    if access_token is None:
        raise InvalidAccessToken

    claims = verifier.verify(SecretStr(access_token))
    session_repository = SQLAlchemySessionRepository(session)
    persisted_session = await session_repository.get_by_id(claims.session_id)
    now = utc_now()
    if (
        persisted_session is None
        or persisted_session.status is not SessionStatus.ACTIVE
        or persisted_session.principal_id != claims.principal_id
        or now >= persisted_session.idle_expires_at
        or now >= persisted_session.absolute_expires_at
    ):
        raise InvalidAccessToken

    principal_repository = SQLAlchemyPrincipalRepository(session)
    principal = await principal_repository.get_by_id(claims.principal_id)
    if (
        principal is None
        or principal.status is not PrincipalStatus.ACTIVE
        or not principal.role.is_human
        or not claims.role.is_human
        or principal.role is not claims.role
    ):
        raise InvalidAccessToken

    requested_scopes = frozenset(security_scopes.scopes)
    if not requested_scopes.issubset(claims.scopes):
        raise InsufficientScopeError

    return AuthenticatedHumanPrincipal(
        principal_id=principal.id,
        session_id=persisted_session.id,
        role=principal.role,
        scopes=claims.scopes,
    )
