"""Typer entrypoint for local service operation."""

from __future__ import annotations

import typer
import uvicorn

from api.application import create_application
from configuration import Settings

cli = typer.Typer(
    name="authservice",
    help="Operate the PokerLost authService locally.",
    no_args_is_help=True,
)


@cli.command()
def run() -> None:
    """Run one local Uvicorn development worker."""
    settings = Settings()
    uvicorn.run(
        create_application(settings),
        host=settings.http.host,
        port=settings.http.port,
        workers=1,
        access_log=True,
    )
