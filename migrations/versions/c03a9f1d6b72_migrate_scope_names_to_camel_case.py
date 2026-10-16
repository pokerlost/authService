"""Migration: migrate OAuth2 scope names to lowerCamelCase segments.

Revision ID: c03a9f1d6b72
Revises: b02d7e4f8a51
Create Date: 2026-09-01
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "c03a9f1d6b72"
down_revision: str | Sequence[str] | None = "b02d7e4f8a51"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_SCOPE_NAME_MIGRATION: Mapping[str, str] = {
    "accounts.self.update_nickname": "accounts.self.updateNickname",
    "accounts.master.create_staff": "accounts.master.createStaff",
    "accounts.master.assign_role": "accounts.master.assignRole",
    "auth.master.manage_clients": "auth.master.manageClients",
    "auth.master.manage_roles": "auth.master.manageRoles",
    "auth.master.manage_scopes": "auth.master.manageScopes",
    "auth.internal.provision_human": "auth.internal.provisionHuman",
    "auth.internal.set_principal_status": "auth.internal.setPrincipalStatus",
    "auth.internal.assign_role": "auth.internal.assignRole",
    "auth.internal.issue_login_grant": "auth.internal.issueLoginGrant",
}

_CAMEL_CASE_SCOPE_PATTERN = "^[a-z][A-Za-z0-9]*([.][a-z][A-Za-z0-9]*)+$"
_LEGACY_SCOPE_PATTERN = "^[a-z][a-z0-9_]*([.][a-z][a-z0-9_]*)+$"


def _replace_scope_names(names: Mapping[str, str]) -> None:
    scope_table = sa.table(
        "oauth_scopes",
        sa.column("name", sa.Text()),
        sa.column("updated_at", sa.DateTime(timezone=True)),
    )
    result = op.get_bind().execute(
        scope_table.update()
        .where(scope_table.c.name.in_(tuple(names)))
        .values(
            name=sa.case(names, value=scope_table.c.name),
            updated_at=sa.func.now(),
        ),
    )
    if result.rowcount != len(names):
        raise RuntimeError("Expected OAuth2 scope rows were not migrated")


def upgrade() -> None:
    """Replace ten seeded scope names without changing their IDs or grant references."""
    op.drop_constraint(
        "ck_oauth_scopes_name_format",
        "oauth_scopes",
        type_="check",
    )
    _replace_scope_names(_SCOPE_NAME_MIGRATION)
    op.create_check_constraint(
        "ck_oauth_scopes_name_format",
        "oauth_scopes",
        f"name ~ '{_CAMEL_CASE_SCOPE_PATTERN}'",
    )


def downgrade() -> None:
    """Restore the prior persisted scope spellings and validation grammar."""
    op.drop_constraint(
        "ck_oauth_scopes_name_format",
        "oauth_scopes",
        type_="check",
    )
    _replace_scope_names({current: previous for previous, current in _SCOPE_NAME_MIGRATION.items()})
    op.create_check_constraint(
        "ck_oauth_scopes_name_format",
        "oauth_scopes",
        f"name ~ '{_LEGACY_SCOPE_PATTERN}'",
    )
