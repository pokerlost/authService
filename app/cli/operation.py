"""Shared safe execution boundary for asynchronous operator commands."""

from __future__ import annotations

import asyncio
from collections.abc import Coroutine

import typer
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError

from application.errors import ApplicationError


def run_operator_operation[ResultT](operation: Coroutine[object, object, ResultT]) -> ResultT:
    """Execute one async operator operation with sanitized expected failures."""
    try:
        return asyncio.run(operation)
    except ApplicationError as exception:
        typer.echo(f"{exception.error_code}: {exception.public_message}", err=True)
        raise typer.Exit(code=1) from None
    except ValidationError:
        typer.echo("AUTH_VALIDATION_ERROR: Operator input validation failed.", err=True)
        raise typer.Exit(code=2) from None
    except (OSError, SQLAlchemyError):
        typer.echo("AUTH_DATABASE_ERROR: Database operation failed.", err=True)
        raise typer.Exit(code=1) from None
