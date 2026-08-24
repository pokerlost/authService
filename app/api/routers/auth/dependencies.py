"""Authentication operation dependency composition."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends, Security

from api.dependencies import DatabaseSession
from api.dependencies.authentication import authenticate_human_principal
from application.authentication import AuthenticatedHumanPrincipal
from application.sessions import (
    RevokeAllSessionsHandler,
    RevokeCurrentSessionHandler,
)
from persistence.repositories import (
    SQLAlchemyAuditEventRepository,
    SQLAlchemyRefreshTokenRepository,
    SQLAlchemySessionRepository,
)


def provide_revoke_current_session_handler(
    session: DatabaseSession,
) -> RevokeCurrentSessionHandler:
    """Compose current-session logout persistence collaborators."""
    return RevokeCurrentSessionHandler(
        session_repository=SQLAlchemySessionRepository(session),
        refresh_token_repository=SQLAlchemyRefreshTokenRepository(session),
        audit_repository=SQLAlchemyAuditEventRepository(session),
    )


type RevokeCurrentSessionHandlerDep = Annotated[
    RevokeCurrentSessionHandler,
    Depends(provide_revoke_current_session_handler),
]


def provide_revoke_all_sessions_handler(
    session: DatabaseSession,
) -> RevokeAllSessionsHandler:
    """Compose principal-isolated set-based logout-all persistence."""
    return RevokeAllSessionsHandler(
        session_repository=SQLAlchemySessionRepository(session),
        refresh_token_repository=SQLAlchemyRefreshTokenRepository(session),
        audit_repository=SQLAlchemyAuditEventRepository(session),
    )


type RevokeAllSessionsHandlerDep = Annotated[
    RevokeAllSessionsHandler,
    Depends(provide_revoke_all_sessions_handler),
]

type LogoutPrincipalDep = Annotated[
    AuthenticatedHumanPrincipal,
    Security(authenticate_human_principal, scopes=["authService.auth.logout"]),
]

type LogoutAllPrincipalDep = Annotated[
    AuthenticatedHumanPrincipal,
    Security(authenticate_human_principal, scopes=["authService.auth.logoutAll"]),
]
