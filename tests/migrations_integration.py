"""Historical revisions run only in a database created and owned by this test."""

from __future__ import annotations

import asyncio
import os
import subprocess
import sys
from collections.abc import Iterator
from pathlib import Path
from uuid import uuid4

import asyncpg
import pytest
from sqlalchemy.engine import make_url


class MigrationDatabase:
    def __init__(self, url: str) -> None:
        self.url = url

    def query(self, sql: str) -> list[tuple[object, ...]]:
        async def execute() -> list[tuple[object, ...]]:
            connection = await asyncpg.connect(self.url)
            try:
                if sql.lstrip().startswith("SELECT"):
                    return [tuple(row) for row in await connection.fetch(sql)]
                await connection.execute(sql)
                return []
            finally:
                await connection.close()

        return asyncio.run(execute())

    def migrate(
        self, direction: str, revision: str, *, error: str | None = None
    ) -> None:
        result = subprocess.run(
            [sys.executable, "-m", "alembic", direction, revision],
            cwd=Path(__file__).resolve().parents[1],
            env={
                **os.environ,
                "DATABASE_URL": self.url.replace(
                    "postgresql://", "postgresql+asyncpg://", 1
                ),
            },
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        if error is None:
            assert result.returncode == 0, result.stdout + result.stderr
        else:
            assert result.returncode != 0
            assert error in result.stderr


@pytest.fixture
def database() -> Iterator[MigrationDatabase]:
    control_url = (
        make_url(os.environ["TEST_DATABASE_URL"])
        .set(drivername="postgresql")
        .render_as_string(hide_password=False)
    )
    # The name contains only this reserved prefix and a locally generated UUID.
    name = "migration_test_" + uuid4().hex

    async def control(sql: str) -> None:
        connection = await asyncpg.connect(control_url)
        try:
            await connection.execute(sql)
        finally:
            await connection.close()

    asyncio.run(control(f'CREATE DATABASE "{name}"'))
    try:
        yield MigrationDatabase(
            make_url(control_url)
            .set(database=name)
            .render_as_string(hide_password=False)
        )
    finally:
        asyncio.run(control(f'DROP DATABASE "{name}" WITH (FORCE)'))


def test_empty_historical_chain_round_trip(database: MigrationDatabase) -> None:
    database.migrate("upgrade", "head")
    assert database.query("SELECT version_num FROM alembic_version") == [
        ("e05f3c8d9b14",)
    ]
    database.migrate("downgrade", "base")
    assert database.query(
        "SELECT tablename FROM pg_tables WHERE schemaname='public' ORDER BY tablename"
    ) == [("alembic_version",)]
    database.migrate("upgrade", "head")
    assert database.query("SELECT version_num FROM alembic_version") == [
        ("e05f3c8d9b14",)
    ]


def test_grants_and_audiences_survive_role_conversion(
    database: MigrationDatabase,
) -> None:
    database.migrate("upgrade", "d04e2b7c8a93")
    database.query("""
        INSERT INTO authorization_principals
            (principal_type, role_id, status, account_id, service_slug)
        SELECT 'human', id, 'active', gen_random_uuid(), NULL
        FROM authorization_roles WHERE code <> 'auto';
        INSERT INTO authorization_principals
            (principal_type, role_id, status, service_slug)
        SELECT 'service', id, 'active', 'accountsService'
        FROM authorization_roles WHERE code = 'auto';
        INSERT INTO service_scope_grants (principal_id, scope_id)
        SELECT id, '20000000-0000-4000-8000-000000000011'::uuid
        FROM authorization_principals WHERE principal_type='service';
        INSERT INTO service_audience_grants (principal_id, audience)
        SELECT id, 'urn:pokerlost:service:authService'
        FROM authorization_principals WHERE principal_type='service';
    """)
    before = database.query(
        "SELECT id, role_id FROM authorization_principals ORDER BY id"
    )
    database.migrate("upgrade", "head")
    assert database.query("""
        SELECT count(*) FROM principal_scope_grants GROUP BY principal_id
        ORDER BY count(*)
    """) == [(1,), (2,), (3,), (10,)]
    assert database.query("SELECT audience FROM principal_audience_grants") == [
        ("authService",)
    ]
    database.migrate("downgrade", "d04e2b7c8a93")
    assert (
        database.query("SELECT id, role_id FROM authorization_principals ORDER BY id")
        == before
    )
    assert database.query("SELECT audience FROM service_audience_grants") == [
        ("urn:pokerlost:service:authService",)
    ]


def test_lossy_human_downgrade_is_atomic(database: MigrationDatabase) -> None:
    database.migrate("upgrade", "head")
    database.query("""
        INSERT INTO authorization_principals (principal_type, status, account_id)
        VALUES ('human', 'active', gen_random_uuid())
    """)
    before = database.query("SELECT * FROM authorization_principals")
    database.migrate(
        "downgrade", "d04e2b7c8a93", error="scopes do not match one legacy role"
    )
    assert database.query("SELECT * FROM authorization_principals") == before
    assert database.query("SELECT version_num FROM alembic_version") == [
        ("e05f3c8d9b14",)
    ]


@pytest.mark.parametrize(
    "change, message",
    [
        (
            "UPDATE oauth_scopes SET name='custom.read' WHERE "
            "id='20000000-0000-4000-8000-000000000001'",
            "was not found exactly once",
        ),
        (
            "INSERT INTO oauth_scopes (name, description) "
            "VALUES ('accounts.self.getMe', 'Synthetic collision')",
            "already exists",
        ),
    ],
)
def test_scope_catalog_failure_preserves_legacy_schema(
    database: MigrationDatabase, change: str, message: str
) -> None:
    database.migrate("upgrade", "d04e2b7c8a93")
    database.query(change)
    before = database.query("SELECT id, name FROM oauth_scopes ORDER BY id")
    database.migrate("upgrade", "head", error=message)
    assert database.query("SELECT id, name FROM oauth_scopes ORDER BY id") == before
    assert database.query("SELECT version_num FROM alembic_version") == [
        ("d04e2b7c8a93",)
    ]
