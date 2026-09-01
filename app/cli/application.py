"""Small Typer interface for local service startup."""

from __future__ import annotations

import asyncio
from typing import Annotated, Never
from uuid import UUID

import typer
import uvicorn
from pydantic import ValidationError
from pypokerlost.types import parse_oauth_scope_string
from sqlalchemy.exc import OperationalError, SQLAlchemyError

from application.errors import ApplicationError
from application.oauth2.bootstrap_service_client import (
    BootstrapServiceClientCommand,
    BootstrapServiceClientHandler,
    BootstrapServiceClientResult,
)
from configuration import Settings
from domain.resource_indicator import ResourceIndicator
from persistence.database import create_database_engine, create_session_factory
from persistence.queries import SQLAlchemyRoleScopeQuery
from persistence.repositories import (
    SQLAlchemyAuthorizationPrincipalRepository,
    SQLAlchemyOAuthClientRepository,
)
from security import SHA256OAuthClientSecretProcessor
from service import SERVICE_NAME, SERVICE_SLUG

cli = typer.Typer(
    name=SERVICE_SLUG,
    help=f"Run the {SERVICE_NAME} service locally.",
    no_args_is_help=True,
)


@cli.callback()
def operator_cli() -> None:
    """Expose development and service-owned operator commands."""


@cli.command()
def run(
    host: Annotated[
        str | None,
        typer.Option(help="HTTP bind host override."),
    ] = None,
    port: Annotated[
        int | None,
        typer.Option(min=1, max=65535, help="HTTP bind port override."),
    ] = None,
    reload: Annotated[
        bool,
        typer.Option(help="Reload the local server when source files change."),
    ] = False,
) -> None:
    """Start one local Uvicorn development worker."""
    settings = Settings()
    uvicorn.run(
        "api.application:create_app",
        factory=True,
        host=host if host is not None else settings.http.host,
        port=port if port is not None else settings.http.port,
        workers=1,
        reload=reload,
        access_log=False,
    )


@cli.command("bootstrap-service-client")
def bootstrap_service_client(
    service_slug: Annotated[
        str,
        typer.Option(help="Exact service principal binding."),
    ],
    scope: Annotated[
        list[str] | None,
        typer.Option("--scope", help="Exact OAuth2 scope grant; repeat for each scope."),
    ] = None,
    resource: Annotated[
        list[str] | None,
        typer.Option("--resource", help="Exact service resource grant; repeat for each target."),
    ] = None,
    client_id: Annotated[
        str | None,
        typer.Option(help="Optional canonical lowercase hyphenated UUID."),
    ] = None,
) -> None:
    """Create one service principal and confidential client transactionally."""
    try:
        command = _build_bootstrap_command(
            service_slug=service_slug,
            scope_values=scope,
            resource_values=resource,
            client_id_value=client_id,
        )
    except ValidationError, ValueError:
        _exit_with_error("Bootstrap input is invalid.")

    try:
        settings = Settings()
    except ValidationError, ValueError:
        _exit_with_error("Runtime configuration is invalid.")

    try:
        result = asyncio.run(_execute_bootstrap(settings, command))
    except OperationalError:
        _exit_with_error("Database is unavailable.")
    except ApplicationError as exception:
        _exit_with_error(exception.public_message)
    except SQLAlchemyError:
        _exit_with_error("Database operation failed.")
    except RuntimeError, ValueError:
        _exit_with_error("Service client bootstrap failed.")
    except Exception:
        _exit_with_error("Service client bootstrap failed.")

    typer.echo(f"client_id={result.client_id}")
    typer.echo(f"client_secret={result.client_secret.get_secret_value()}")


def _build_bootstrap_command(
    *,
    service_slug: str,
    scope_values: list[str] | None,
    resource_values: list[str] | None,
    client_id_value: str | None,
) -> BootstrapServiceClientCommand:
    """Validate exact operator values before opening a database transaction."""
    if not service_slug.strip():
        raise ValueError("Service slug is empty")
    if not scope_values or len(set(scope_values)) != len(scope_values):
        raise ValueError("Scopes are missing or duplicated")
    if not resource_values or len(set(resource_values)) != len(resource_values):
        raise ValueError("Resources are missing or duplicated")

    parsed_client_id: UUID | None = None
    if client_id_value is not None:
        try:
            parsed_client_id = UUID(client_id_value)
        except ValueError:
            raise ValueError("Client identifier is invalid") from None
        if str(parsed_client_id) != client_id_value:
            raise ValueError("Client identifier is not canonical")

    return BootstrapServiceClientCommand(
        service_slug=service_slug,
        client_id=parsed_client_id,
        scopes=parse_oauth_scope_string(" ".join(scope_values)),
        resources=tuple(ResourceIndicator.parse(value) for value in resource_values),
    )


async def _execute_bootstrap(
    settings: Settings,
    command: BootstrapServiceClientCommand,
) -> BootstrapServiceClientResult:
    """Own one local PostgreSQL transaction and dispose its engine."""
    engine = create_database_engine(settings.database, application_name=f"{SERVICE_NAME}-bootstrap")
    session_factory = create_session_factory(engine)
    try:
        async with session_factory.begin() as session:
            handler = BootstrapServiceClientHandler(
                SQLAlchemyAuthorizationPrincipalRepository(session),
                SQLAlchemyOAuthClientRepository(session),
                SQLAlchemyRoleScopeQuery(session),
                SHA256OAuthClientSecretProcessor(),
            )
            return await handler(command)
    finally:
        await engine.dispose()


def _exit_with_error(message: str) -> Never:
    """Print one safe operator failure and terminate without a traceback."""
    typer.echo(f"error: {message}", err=True)
    raise typer.Exit(code=1)
