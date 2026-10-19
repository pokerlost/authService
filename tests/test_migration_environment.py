"""Offline migration rejection never needs a database connection."""

from __future__ import annotations

import os
import subprocess
import sys


def test_offline_migration_fails_before_connecting() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head", "--sql"],
        env={
            **os.environ,
            "DATABASE_URL": "postgresql+asyncpg://unused:unused@127.0.0.1:1/unused",
        },
        capture_output=True,
        text=True,
        timeout=15,
        check=False,
    )
    assert result.returncode != 0
    assert "Offline migrations are not configured" in result.stderr
