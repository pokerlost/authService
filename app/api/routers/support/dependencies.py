"""Support-safe dependency composition."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends, Security

from api.dependencies import DatabaseSession
from api.dependencies.authentication import authenticate_human_principal
from application.authentication import AuthenticatedHumanPrincipal
from application.support import GetUserAccountHandler
from persistence.repositories import SQLAlchemyHumanAccountRepository


def provide_get_user_account_handler(session: DatabaseSession) -> GetUserAccountHandler:
    """Compose ordinary-user support lookup on one request transaction."""
    return GetUserAccountHandler(SQLAlchemyHumanAccountRepository(session))


type GetUserAccountHandlerDep = Annotated[
    GetUserAccountHandler,
    Depends(provide_get_user_account_handler),
]

type GetUserAccountPrincipalDep = Annotated[
    AuthenticatedHumanPrincipal,
    Security(authenticate_human_principal, scopes=["authService.support.getUserAccount"]),
]
