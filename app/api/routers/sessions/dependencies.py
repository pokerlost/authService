"""Human session-management dependency composition."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends, Security

from api.dependencies import DatabaseSession
from api.dependencies.authentication import authenticate_human_principal
from application.authentication import AuthenticatedHumanPrincipal
from application.sessions import ListSessionsHandler, RevokeSessionHandler
from persistence.repositories import (
    SQLAlchemyAuditEventRepository,
    SQLAlchemyRefreshTokenRepository,
    SQLAlchemySessionRepository,
)


def provide_list_sessions_handler(session: DatabaseSession) -> ListSessionsHandler:
    """Compose owned session listing on the request database session."""
    return ListSessionsHandler(SQLAlchemySessionRepository(session))


type ListSessionsHandlerDep = Annotated[
    ListSessionsHandler,
    Depends(provide_list_sessions_handler),
]


def provide_revoke_session_handler(session: DatabaseSession) -> RevokeSessionHandler:
    """Compose owned session revocation persistence collaborators."""
    return RevokeSessionHandler(
        session_repository=SQLAlchemySessionRepository(session),
        refresh_token_repository=SQLAlchemyRefreshTokenRepository(session),
        audit_repository=SQLAlchemyAuditEventRepository(session),
    )


type RevokeSessionHandlerDep = Annotated[
    RevokeSessionHandler,
    Depends(provide_revoke_session_handler),
]

type ListSessionsPrincipalDep = Annotated[
    AuthenticatedHumanPrincipal,
    Security(authenticate_human_principal, scopes=["authService.sessions.list"]),
]

type RevokeSessionPrincipalDep = Annotated[
    AuthenticatedHumanPrincipal,
    Security(authenticate_human_principal, scopes=["authService.sessions.revoke"]),
]
