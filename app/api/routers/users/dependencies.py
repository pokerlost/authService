"""User operation dependency composition."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_database_session, get_settings
from application.security import Argon2PasswordHasher
from application.users import RegisterUserHandler
from configuration import Settings
from persistence.repositories import (
    SQLAlchemyHumanAccountRepository,
    SQLAlchemyPasswordCredentialRepository,
    SQLAlchemyPrincipalRepository,
)


def provide_register_user(
    settings: Annotated[Settings, Depends(get_settings)],
    session: Annotated[
        AsyncSession,
        Depends(get_database_session, scope="function"),
    ],
) -> RegisterUserHandler:
    """Compose registration collaborators around one request transaction."""
    password = settings.password
    return RegisterUserHandler(
        principal_repository=SQLAlchemyPrincipalRepository(session),
        human_account_repository=SQLAlchemyHumanAccountRepository(session),
        password_credential_repository=SQLAlchemyPasswordCredentialRepository(session),
        password_hasher=Argon2PasswordHasher(
            time_cost=password.time_cost,
            memory_cost_kib=password.memory_cost_kib,
            parallelism=password.parallelism,
            hash_length=password.hash_length,
            salt_length=password.salt_length,
        ),
    )
