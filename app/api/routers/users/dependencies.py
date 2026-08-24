"""User operation dependency composition."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends

from api.dependencies import ApplicationResourcesDep, DatabaseSession
from application.accounts import CreateHumanAccountHandler
from application.users import RegisterUserHandler
from persistence.repositories import (
    SQLAlchemyAuditEventRepository,
    SQLAlchemyHumanAccountRepository,
    SQLAlchemyPasswordCredentialRepository,
    SQLAlchemyPrincipalRepository,
)


def provide_register_user_handler(
    session: DatabaseSession,
    resources: ApplicationResourcesDep,
) -> RegisterUserHandler:
    """Compose ordinary-user registration with one request transaction."""
    return RegisterUserHandler(
        CreateHumanAccountHandler(
            principal_repository=SQLAlchemyPrincipalRepository(session),
            human_account_repository=SQLAlchemyHumanAccountRepository(session),
            password_credential_repository=SQLAlchemyPasswordCredentialRepository(session),
            audit_repository=SQLAlchemyAuditEventRepository(session),
            password_hasher=resources.password_hasher,
        ),
    )


type RegisterUserHandlerDep = Annotated[
    RegisterUserHandler,
    Depends(provide_register_user_handler),
]
