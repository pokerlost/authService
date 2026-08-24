"""Operator commands for explicit OAuth2 scope grant management."""

from __future__ import annotations

from typing import Annotated

import typer

from application.audit import AuditContext
from application.scope_grants import (
    GrantRoleScopeCommand,
    GrantRoleScopeHandler,
    GrantServiceScopeCommand,
    GrantServiceScopeHandler,
    RevokeRoleScopeCommand,
    RevokeRoleScopeHandler,
    RevokeServiceScopeCommand,
    RevokeServiceScopeHandler,
)
from configuration import Settings
from domain.enums import Role
from persistence.database import create_database_engine, create_session_factory
from persistence.queries import SQLAlchemyScopeQuery
from persistence.repositories import (
    SQLAlchemyAuditEventRepository,
    SQLAlchemyRoleScopeGrantRepository,
    SQLAlchemyServiceAudienceGrantRepository,
    SQLAlchemyServicePrincipalRepository,
    SQLAlchemyServiceScopeGrantRepository,
)

from .operation import run_operator_operation

oauth_cli = typer.Typer(
    name="oauth",
    help="Manage explicit human role and machine service OAuth2 scope grants.",
    no_args_is_help=True,
)


async def _grant_role_scope(*, role: Role, scope: str) -> None:
    settings = Settings()
    engine = create_database_engine(
        settings.database,
        application_name=settings.application.service_name,
    )
    try:
        session_factory = create_session_factory(engine)
        async with session_factory.begin() as session:
            await GrantRoleScopeHandler(
                grant_repository=SQLAlchemyRoleScopeGrantRepository(session),
                scope_query=SQLAlchemyScopeQuery(session),
                audit_repository=SQLAlchemyAuditEventRepository(session),
            ).execute(
                GrantRoleScopeCommand(
                    role=role,
                    scope=scope,
                    audit_context=AuditContext(),
                )
            )
    finally:
        await engine.dispose()


async def _revoke_role_scope(*, role: Role, scope: str) -> None:
    settings = Settings()
    engine = create_database_engine(
        settings.database,
        application_name=settings.application.service_name,
    )
    try:
        session_factory = create_session_factory(engine)
        async with session_factory.begin() as session:
            await RevokeRoleScopeHandler(
                grant_repository=SQLAlchemyRoleScopeGrantRepository(session),
                audit_repository=SQLAlchemyAuditEventRepository(session),
            ).execute(
                RevokeRoleScopeCommand(
                    role=role,
                    scope=scope,
                    audit_context=AuditContext(),
                )
            )
    finally:
        await engine.dispose()


async def _grant_service_scope(
    *,
    service_slug: str,
    audience: str,
    scope: str,
) -> None:
    settings = Settings()
    engine = create_database_engine(
        settings.database,
        application_name=settings.application.service_name,
    )
    try:
        session_factory = create_session_factory(engine)
        async with session_factory.begin() as session:
            await GrantServiceScopeHandler(
                service_principal_repository=SQLAlchemyServicePrincipalRepository(session),
                audience_repository=SQLAlchemyServiceAudienceGrantRepository(session),
                grant_repository=SQLAlchemyServiceScopeGrantRepository(session),
                scope_query=SQLAlchemyScopeQuery(session),
                audit_repository=SQLAlchemyAuditEventRepository(session),
            ).execute(
                GrantServiceScopeCommand(
                    service_slug=service_slug,
                    audience=audience,
                    scope=scope,
                    audit_context=AuditContext(),
                )
            )
    finally:
        await engine.dispose()


async def _revoke_service_scope(
    *,
    service_slug: str,
    audience: str,
    scope: str,
) -> None:
    settings = Settings()
    engine = create_database_engine(
        settings.database,
        application_name=settings.application.service_name,
    )
    try:
        session_factory = create_session_factory(engine)
        async with session_factory.begin() as session:
            await RevokeServiceScopeHandler(
                service_principal_repository=SQLAlchemyServicePrincipalRepository(session),
                grant_repository=SQLAlchemyServiceScopeGrantRepository(session),
                audit_repository=SQLAlchemyAuditEventRepository(session),
            ).execute(
                RevokeServiceScopeCommand(
                    service_slug=service_slug,
                    audience=audience,
                    scope=scope,
                    audit_context=AuditContext(),
                )
            )
    finally:
        await engine.dispose()


@oauth_cli.command("grant-role-scope")
def grant_role_scope(
    role: Annotated[Role, typer.Argument(help="Exact human role: user, support, or master.")],
    scope: Annotated[str, typer.Argument(help="Canonical operationId scope.")],
) -> None:
    """Grant one active canonical operation scope to one exact human role."""
    run_operator_operation(_grant_role_scope(role=role, scope=scope))
    typer.echo("Role scope granted.")


@oauth_cli.command("revoke-role-scope")
def revoke_role_scope(
    role: Annotated[Role, typer.Argument(help="Exact human role: user, support, or master.")],
    scope: Annotated[str, typer.Argument(help="Canonical operationId scope.")],
) -> None:
    """Idempotently revoke one exact human role scope."""
    run_operator_operation(_revoke_role_scope(role=role, scope=scope))
    typer.echo("Role scope revoked.")


@oauth_cli.command("grant-service-scope")
def grant_service_scope(
    service_slug: Annotated[str, typer.Argument(help="Canonical source SERVICE_SLUG.")],
    audience: Annotated[str, typer.Argument(help="Canonical target SERVICE_SLUG.")],
    scope: Annotated[str, typer.Argument(help="Canonical target operationId scope.")],
) -> None:
    """Grant one resource-owned scope to one service and audience."""
    run_operator_operation(
        _grant_service_scope(
            service_slug=service_slug,
            audience=audience,
            scope=scope,
        )
    )
    typer.echo("Service scope granted.")


@oauth_cli.command("revoke-service-scope")
def revoke_service_scope(
    service_slug: Annotated[str, typer.Argument(help="Canonical source SERVICE_SLUG.")],
    audience: Annotated[str, typer.Argument(help="Canonical target SERVICE_SLUG.")],
    scope: Annotated[str, typer.Argument(help="Canonical target operationId scope.")],
) -> None:
    """Idempotently revoke one service scope grant."""
    run_operator_operation(
        _revoke_service_scope(
            service_slug=service_slug,
            audience=audience,
            scope=scope,
        )
    )
    typer.echo("Service scope revoked.")
