"""Master control-plane dependency composition."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends

from api.dependencies import ApplicationResourcesDep, DatabaseSession
from application.accounts import (
    CreateHumanAccountHandler,
    DisableHumanAccountHandler,
    EnableHumanAccountHandler,
    ResetHumanPasswordHandler,
)
from persistence.repositories import (
    SQLAlchemyAuditEventRepository,
    SQLAlchemyHumanAccountRepository,
    SQLAlchemyPasswordCredentialRepository,
    SQLAlchemyPrincipalRepository,
    SQLAlchemyRefreshTokenRepository,
    SQLAlchemySessionRepository,
)


def provide_create_human_account_handler(
    session: DatabaseSession,
    resources: ApplicationResourcesDep,
) -> CreateHumanAccountHandler:
    """Compose trusted staff account creation in one request transaction."""
    return CreateHumanAccountHandler(
        principal_repository=SQLAlchemyPrincipalRepository(session),
        human_account_repository=SQLAlchemyHumanAccountRepository(session),
        password_credential_repository=SQLAlchemyPasswordCredentialRepository(session),
        audit_repository=SQLAlchemyAuditEventRepository(session),
        password_hasher=resources.password_hasher,
    )


type CreateHumanAccountHandlerDep = Annotated[
    CreateHumanAccountHandler,
    Depends(provide_create_human_account_handler),
]


def provide_disable_human_account_handler(
    session: DatabaseSession,
) -> DisableHumanAccountHandler:
    """Compose human disable and session-family revocation collaborators."""
    return DisableHumanAccountHandler(
        principal_repository=SQLAlchemyPrincipalRepository(session),
        session_repository=SQLAlchemySessionRepository(session),
        refresh_token_repository=SQLAlchemyRefreshTokenRepository(session),
        audit_repository=SQLAlchemyAuditEventRepository(session),
    )


type DisableHumanAccountHandlerDep = Annotated[
    DisableHumanAccountHandler,
    Depends(provide_disable_human_account_handler),
]


def provide_enable_human_account_handler(
    session: DatabaseSession,
) -> EnableHumanAccountHandler:
    """Compose a locked human principal enable transition."""
    return EnableHumanAccountHandler(
        principal_repository=SQLAlchemyPrincipalRepository(session),
        audit_repository=SQLAlchemyAuditEventRepository(session),
    )


type EnableHumanAccountHandlerDep = Annotated[
    EnableHumanAccountHandler,
    Depends(provide_enable_human_account_handler),
]


def provide_reset_human_password_handler(
    session: DatabaseSession,
    resources: ApplicationResourcesDep,
) -> ResetHumanPasswordHandler:
    """Compose a master-assisted credential replacement transaction."""
    return ResetHumanPasswordHandler(
        principal_repository=SQLAlchemyPrincipalRepository(session),
        password_credential_repository=SQLAlchemyPasswordCredentialRepository(session),
        session_repository=SQLAlchemySessionRepository(session),
        refresh_token_repository=SQLAlchemyRefreshTokenRepository(session),
        audit_repository=SQLAlchemyAuditEventRepository(session),
        password_hasher=resources.password_hasher,
    )


type ResetHumanPasswordHandlerDep = Annotated[
    ResetHumanPasswordHandler,
    Depends(provide_reset_human_password_handler),
]
