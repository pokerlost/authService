"""Alembic connection wiring; add domain metadata only with an actual schema."""

from __future__ import annotations

import asyncio

from alembic import context
from sqlalchemy.engine import Connection

from authService.persistence import createEngine
from authService.settings import ServiceSettings


def runMigrations(connection: Connection) -> None:
    """Run the immutable historical revision chain on one connection."""
    context.configure(connection=connection, target_metadata=None)
    with context.begin_transaction():
        context.run_migrations()


async def runOnlineMigrations() -> None:
    """Own and dispose a dedicated engine for explicit operator migrations."""
    engine = createEngine(ServiceSettings())
    try:
        async with engine.connect() as connection:
            await connection.run_sync(runMigrations)
    finally:
        await engine.dispose()


if context.is_offline_mode():
    raise RuntimeError("Offline migrations are not configured for this empty foundation")
asyncio.run(runOnlineMigrations())
