"""Migration: rename the assign-principal-role scope.

Revision ID: d04e2b7c8a93
Revises: c03a9f1d6b72
Create Date: 2026-09-01
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "d04e2b7c8a93"
down_revision: str | Sequence[str] | None = "c03a9f1d6b72"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_PREVIOUS_SCOPE = "auth.internal.assignRole"
_CURRENT_SCOPE = "auth.internal.assignPrincipalRole"


def _rename_scope(previous: str, current: str) -> None:
    scope_table = sa.table(
        "oauth_scopes",
        sa.column("name", sa.Text()),
        sa.column("updated_at", sa.DateTime(timezone=True)),
    )
    result = op.get_bind().execute(
        scope_table.update()
        .where(scope_table.c.name == previous)
        .values(name=current, updated_at=sa.func.now()),
    )
    if result.rowcount != 1:
        raise RuntimeError("Expected assign-principal-role scope row was not migrated")


def upgrade() -> None:
    """Rename the persisted scope without changing its ID or grant references."""
    _rename_scope(_PREVIOUS_SCOPE, _CURRENT_SCOPE)


def downgrade() -> None:
    """Restore the previous lowerCamelCase scope name."""
    _rename_scope(_CURRENT_SCOPE, _PREVIOUS_SCOPE)
