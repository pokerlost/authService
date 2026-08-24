"""Operator commands for AUTO service identity provisioning."""

from __future__ import annotations

from typing import Annotated

import typer

from application.audit import AuditContext
from application.security import ServiceCredentialProtector
from application.service_authentication import (
    CreatedServiceCredential,
    CreateServiceCredentialCommand,
    CreateServiceCredentialHandler,
    CreateServicePrincipalCommand,
    CreateServicePrincipalHandler,
    GrantServiceAudienceCommand,
    GrantServiceAudienceHandler,
    RevokeServiceAudienceCommand,
    RevokeServiceAudienceHandler,
    RevokeServiceCredentialCommand,
    RevokeServiceCredentialHandler,
)
from configuration import Settings
from persistence.database import create_database_engine, create_session_factory
from persistence.database.models import ServicePrincipalModel
from persistence.repositories import (
    SQLAlchemyAuditEventRepository,
    SQLAlchemyPrincipalRepository,
    SQLAlchemyServiceAudienceGrantRepository,
    SQLAlchemyServiceCredentialRepository,
    SQLAlchemyServicePrincipalRepository,
)

from .operation import run_operator_operation

auto_cli = typer.Typer(
    name="auto",
    help="Provision and revoke AUTO service authentication state.",
    no_args_is_help=True,
)


async def _create_service_principal(service_slug: str) -> ServicePrincipalModel:
    settings = Settings()
    engine = create_database_engine(
        settings.database,
        application_name=settings.application.service_name,
    )
    try:
        session_factory = create_session_factory(engine)
        async with session_factory.begin() as session:
            handler = CreateServicePrincipalHandler(
                principal_repository=SQLAlchemyPrincipalRepository(session),
                service_principal_repository=SQLAlchemyServicePrincipalRepository(session),
                audit_repository=SQLAlchemyAuditEventRepository(session),
            )
            return await handler.execute(
                CreateServicePrincipalCommand(
                    service_slug=service_slug,
                    audit_context=AuditContext(),
                ),
            )
    finally:
        await engine.dispose()


async def _create_service_credential(service_slug: str) -> CreatedServiceCredential:
    settings = Settings()
    engine = create_database_engine(
        settings.database,
        application_name=settings.application.service_name,
    )
    try:
        session_factory = create_session_factory(engine)
        async with session_factory.begin() as session:
            handler = CreateServiceCredentialHandler(
                principal_repository=SQLAlchemyPrincipalRepository(session),
                service_principal_repository=SQLAlchemyServicePrincipalRepository(session),
                service_credential_repository=SQLAlchemyServiceCredentialRepository(session),
                audit_repository=SQLAlchemyAuditEventRepository(session),
                protector=ServiceCredentialProtector(
                    settings.service_auth.credential_pepper,
                ),
                credential_ttl=settings.service_auth.credential_ttl,
            )
            return await handler.execute(
                CreateServiceCredentialCommand(
                    service_slug=service_slug,
                    audit_context=AuditContext(),
                ),
            )
    finally:
        await engine.dispose()


async def _revoke_service_credential(client_id: str) -> None:
    settings = Settings()
    engine = create_database_engine(
        settings.database,
        application_name=settings.application.service_name,
    )
    try:
        session_factory = create_session_factory(engine)
        async with session_factory.begin() as session:
            handler = RevokeServiceCredentialHandler(
                SQLAlchemyServiceCredentialRepository(session),
                audit_repository=SQLAlchemyAuditEventRepository(session),
            )
            await handler.execute(
                RevokeServiceCredentialCommand(
                    client_id=client_id,
                    audit_context=AuditContext(),
                )
            )
    finally:
        await engine.dispose()


async def _grant_service_audience(service_slug: str, audience: str) -> None:
    settings = Settings()
    engine = create_database_engine(
        settings.database,
        application_name=settings.application.service_name,
    )
    try:
        session_factory = create_session_factory(engine)
        async with session_factory.begin() as session:
            handler = GrantServiceAudienceHandler(
                service_principal_repository=SQLAlchemyServicePrincipalRepository(session),
                grant_repository=SQLAlchemyServiceAudienceGrantRepository(session),
                audit_repository=SQLAlchemyAuditEventRepository(session),
            )
            await handler.execute(
                GrantServiceAudienceCommand(
                    service_slug=service_slug,
                    audience=audience,
                    audit_context=AuditContext(),
                ),
            )
    finally:
        await engine.dispose()


async def _revoke_service_audience(service_slug: str, audience: str) -> None:
    settings = Settings()
    engine = create_database_engine(
        settings.database,
        application_name=settings.application.service_name,
    )
    try:
        session_factory = create_session_factory(engine)
        async with session_factory.begin() as session:
            handler = RevokeServiceAudienceHandler(
                service_principal_repository=SQLAlchemyServicePrincipalRepository(session),
                grant_repository=SQLAlchemyServiceAudienceGrantRepository(session),
                audit_repository=SQLAlchemyAuditEventRepository(session),
            )
            await handler.execute(
                RevokeServiceAudienceCommand(
                    service_slug=service_slug,
                    audience=audience,
                    audit_context=AuditContext(),
                ),
            )
    finally:
        await engine.dispose()


@auto_cli.command("create-principal")
def create_principal(
    service_slug: Annotated[
        str,
        typer.Argument(help="Canonical source SERVICE_SLUG."),
    ],
) -> None:
    """Create one active AUTO principal and canonical service identity."""
    service_principal = run_operator_operation(_create_service_principal(service_slug))
    typer.echo(f"principalId={service_principal.principal_id}")
    typer.echo(f"serviceSlug={service_principal.service_slug}")


@auto_cli.command("create-credential")
def create_credential(
    service_slug: Annotated[
        str,
        typer.Argument(help="Canonical source SERVICE_SLUG."),
    ],
) -> None:
    """Create a finite service credential and show its secret once."""
    credential = run_operator_operation(_create_service_credential(service_slug))
    typer.echo(f"clientId={credential.client_id}")
    typer.echo(f"clientSecret={credential.client_secret.get_secret_value()}")
    typer.echo(f"expiresAt={credential.expires_at.isoformat()}")


@auto_cli.command("revoke-credential")
def revoke_credential(
    client_id: Annotated[
        str,
        typer.Argument(help="Public random client ID to revoke."),
    ],
) -> None:
    """Idempotently revoke one known service credential."""
    run_operator_operation(_revoke_service_credential(client_id))
    typer.echo("Service credential revoked.")


@auto_cli.command("grant-audience")
def grant_audience(
    service_slug: Annotated[
        str,
        typer.Argument(help="Canonical source SERVICE_SLUG."),
    ],
    audience: Annotated[
        str,
        typer.Argument(help="Canonical target SERVICE_SLUG audience."),
    ],
) -> None:
    """Idempotently grant one target audience to one source service."""
    run_operator_operation(_grant_service_audience(service_slug, audience))
    typer.echo("Service audience granted.")


@auto_cli.command("revoke-audience")
def revoke_audience(
    service_slug: Annotated[
        str,
        typer.Argument(help="Canonical source SERVICE_SLUG."),
    ],
    audience: Annotated[
        str,
        typer.Argument(help="Canonical target SERVICE_SLUG audience."),
    ],
) -> None:
    """Idempotently revoke one target audience from one source service."""
    run_operator_operation(_revoke_service_audience(service_slug, audience))
    typer.echo("Service audience revoked.")
