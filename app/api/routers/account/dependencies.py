"""Authenticated account dependency composition."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends, Security

from api.dependencies import ApplicationResourcesDep, DatabaseSession
from api.dependencies.authentication import authenticate_human_principal
from application.accounts import ChangePasswordHandler
from application.authentication import AuthenticatedHumanPrincipal
from persistence.repositories import (
    SQLAlchemyAuditEventRepository,
    SQLAlchemyPasswordCredentialRepository,
    SQLAlchemyPrincipalRepository,
    SQLAlchemyRefreshTokenRepository,
    SQLAlchemySessionRepository,
)


def provide_change_password_handler(
    session: DatabaseSession,
    resources: ApplicationResourcesDep,
) -> ChangePasswordHandler:
    """Compose password replacement, session revocation, and durable audit."""
    return ChangePasswordHandler(
        principal_repository=SQLAlchemyPrincipalRepository(session),
        password_credential_repository=SQLAlchemyPasswordCredentialRepository(session),
        session_repository=SQLAlchemySessionRepository(session),
        refresh_token_repository=SQLAlchemyRefreshTokenRepository(session),
        audit_repository=SQLAlchemyAuditEventRepository(session),
        password_hasher=resources.password_hasher,
    )


type ChangePasswordHandlerDep = Annotated[
    ChangePasswordHandler,
    Depends(provide_change_password_handler),
]
type ChangePasswordPrincipalDep = Annotated[
    AuthenticatedHumanPrincipal,
    Security(
        authenticate_human_principal,
        scopes=["authService.account.changePassword"],
    ),
]
