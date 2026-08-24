"""Small Typer interface for local authService startup."""

from __future__ import annotations

from typing import Annotated

import typer
import uvicorn

from configuration import Settings

from .auto import auto_cli
from .maintenance import maintenance_cli
from .master import master_cli
from .oauth import oauth_cli

cli = typer.Typer(
    name="authService",
    help="Run the authService service locally.",
    no_args_is_help=True,
)
cli.add_typer(auto_cli, name="auto")
cli.add_typer(maintenance_cli, name="maintenance")
cli.add_typer(master_cli, name="master")
cli.add_typer(oauth_cli, name="oauth")


@cli.callback()
def operator_cli() -> None:
    """Expose authService operator commands."""


@cli.command()
def run(
    host: Annotated[
        str | None,
        typer.Option(help="HTTP bind host override."),
    ] = None,
    port: Annotated[
        int | None,
        typer.Option(
            min=1,
            max=65535,
            help="HTTP bind port override.",
        ),
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
