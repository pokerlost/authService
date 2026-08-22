"""Typer entrypoint for local service operation."""

from __future__ import annotations

from typing import Annotated

import typer
import uvicorn

from configuration import Settings

cli = typer.Typer(
    name="authservice",
    help="Operate the PokerLost authService locally.",
    no_args_is_help=True,
)


@cli.command()
def run(
    host: Annotated[
        str | None,
        typer.Option(help="Override the configured local bind host."),
    ] = None,
    port: Annotated[
        int | None,
        typer.Option(min=1, max=65_535, help="Override the configured local bind port."),
    ] = None,
    reload: Annotated[
        bool,
        typer.Option("--reload/--no-reload", help="Reload when project files change."),
    ] = True,
) -> None:
    """Run one local Uvicorn development worker from the application factory."""
    settings = Settings()
    uvicorn.run(
        "api.application:create_app",
        factory=True,
        host=host or settings.http.host,
        port=port or settings.http.port,
        reload=reload,
        workers=1,
        access_log=True,
    )
