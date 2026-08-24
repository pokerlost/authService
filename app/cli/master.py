"""Operator bootstrap command for master human identities."""

from __future__ import annotations

import typer
from pydantic import SecretStr

from application.accounts import (
    CreatedHumanAccount,
    CreateHumanAccountCommand,
    CreateHumanAccountHandler,
)
from application.audit import AuditContext
from application.security import Argon2PasswordHasher
from configuration import Settings
from domain.enums import Role
from persistence.database import create_database_engine, create_session_factory
from persistence.repositories import (
    SQLAlchemyAuditEventRepository,
    SQLAlchemyHumanAccountRepository,
    SQLAlchemyPasswordCredentialRepository,
    SQLAlchemyPrincipalRepository,
)

from .operation import run_operator_operation

master_cli = typer.Typer(
    name="master",
    help="Bootstrap trusted master human accounts.",
    no_args_is_help=True,
)


async def _create_master(
    *,
    username: str,
    nickname: str,
    password: SecretStr,
) -> CreatedHumanAccount:
    settings = Settings()
    engine = create_database_engine(
        settings.database,
        application_name=settings.application.service_name,
    )
    try:
        session_factory = create_session_factory(engine)
        async with session_factory.begin() as session:
            handler = CreateHumanAccountHandler(
                principal_repository=SQLAlchemyPrincipalRepository(session),
                human_account_repository=SQLAlchemyHumanAccountRepository(session),
                password_credential_repository=SQLAlchemyPasswordCredentialRepository(session),
                audit_repository=SQLAlchemyAuditEventRepository(session),
                password_hasher=Argon2PasswordHasher(
                    time_cost=settings.password.time_cost,
                    memory_cost_kib=settings.password.memory_cost_kib,
                    parallelism=settings.password.parallelism,
                    hash_length=settings.password.hash_length,
                    salt_length=settings.password.salt_length,
                ),
            )
            return await handler.execute(
                CreateHumanAccountCommand(
                    username=username,
                    nickname=nickname,
                    password=password,
                    role=Role.MASTER,
                    audit_context=AuditContext(),
                ),
            )
    finally:
        await engine.dispose()


@master_cli.command("create")
def create_master() -> None:
    """Create one active master account without establishing a session."""
    username = typer.prompt("Username")
    nickname = typer.prompt("Nickname")
    password = SecretStr(
        typer.prompt(
            "Password",
            hide_input=True,
            confirmation_prompt=True,
        ),
    )
    account = run_operator_operation(
        _create_master(
            username=username,
            nickname=nickname,
            password=password,
        ),
    )
    typer.echo(f"principalId={account.id}")
    typer.echo(f"username={account.username}")
    typer.echo(f"nickname={account.nickname}")
    typer.echo(f"role={account.role}")
