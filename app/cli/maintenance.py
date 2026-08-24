"""Operator commands for bounded security-state retention cleanup."""

from __future__ import annotations

from typing import Annotated

import typer

from application.maintenance import (
    CleanupSecurityStateCommand,
    CleanupSecurityStateHandler,
    CleanupSummary,
)
from configuration import Settings
from persistence.database import create_database_engine, create_session_factory
from persistence.repositories import SQLAlchemySecurityCleanupRepository

from .operation import run_operator_operation

maintenance_cli = typer.Typer(
    name="maintenance",
    help="Run bounded retention maintenance.",
    no_args_is_help=True,
)


async def _cleanup(*, dry_run: bool) -> CleanupSummary:
    settings = Settings()
    engine = create_database_engine(
        settings.database,
        application_name=settings.application.service_name,
    )
    try:
        session_factory = create_session_factory(engine)
        async with session_factory.begin() as session:
            handler = CleanupSecurityStateHandler(SQLAlchemySecurityCleanupRepository(session))
            return await handler.execute(
                CleanupSecurityStateCommand(
                    batch_size=settings.maintenance.cleanup_batch_size,
                    security_state_retention_days=(
                        settings.maintenance.security_state_retention_days
                    ),
                    audit_retention_days=settings.maintenance.audit_retention_days,
                    dry_run=dry_run,
                )
            )
    finally:
        await engine.dispose()


@maintenance_cli.command("cleanup")
def cleanup(
    dry_run: Annotated[
        bool,
        typer.Option(
            "--dry-run/--apply",
            help="Report one bounded batch without deleting, or explicitly apply it.",
        ),
    ] = True,
) -> None:
    """Clean only configured retention-eligible security state in bounded batches."""
    summary = run_operator_operation(_cleanup(dry_run=dry_run))
    typer.echo(f"dryRun={str(summary.dry_run).lower()}")
    typer.echo(f"refreshTokens={summary.refresh_tokens}")
    typer.echo(f"sessions={summary.sessions}")
    typer.echo(f"serviceCredentials={summary.service_credentials}")
    typer.echo(f"rateLimitRows={summary.rate_limit_rows}")
    typer.echo(f"auditEvents={summary.audit_events}")
