"""Migration: create authorization foundation.

Revision ID: a01f6b2c9d34
Revises: None
Create Date: 2026-08-29
"""

from __future__ import annotations

from collections.abc import Sequence
from uuid import UUID

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "a01f6b2c9d34"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


_ROLE_IDS = {
    "user": UUID("10000000-0000-4000-8000-000000000001"),
    "support": UUID("10000000-0000-4000-8000-000000000002"),
    "master": UUID("10000000-0000-4000-8000-000000000003"),
    "auto": UUID("10000000-0000-4000-8000-000000000004"),
}

_SCOPE_IDS = {
    "accounts.self.read": UUID("20000000-0000-4000-8000-000000000001"),
    "accounts.self.update_nickname": UUID("20000000-0000-4000-8000-000000000002"),
    "accounts.support.read": UUID("20000000-0000-4000-8000-000000000003"),
    "accounts.master.create_staff": UUID("20000000-0000-4000-8000-000000000004"),
    "accounts.master.disable": UUID("20000000-0000-4000-8000-000000000005"),
    "accounts.master.enable": UUID("20000000-0000-4000-8000-000000000006"),
    "accounts.master.assign_role": UUID("20000000-0000-4000-8000-000000000007"),
    "auth.master.manage_clients": UUID("20000000-0000-4000-8000-000000000008"),
    "auth.master.manage_roles": UUID("20000000-0000-4000-8000-000000000009"),
    "auth.master.manage_scopes": UUID("20000000-0000-4000-8000-000000000010"),
    "auth.internal.provision_human": UUID("20000000-0000-4000-8000-000000000011"),
    "auth.internal.set_principal_status": UUID("20000000-0000-4000-8000-000000000012"),
    "auth.internal.assign_role": UUID("20000000-0000-4000-8000-000000000013"),
    "auth.internal.issue_login_grant": UUID("20000000-0000-4000-8000-000000000014"),
}

_SCOPE_DESCRIPTIONS = {
    "accounts.self.read": "Read the current human account.",
    "accounts.self.update_nickname": "Update the current account nickname.",
    "accounts.support.read": "Read support-safe account information.",
    "accounts.master.create_staff": "Create a staff account.",
    "accounts.master.disable": "Disable a human account.",
    "accounts.master.enable": "Enable a human account.",
    "accounts.master.assign_role": "Assign a human authorization role.",
    "auth.master.manage_clients": "Manage OAuth2 clients.",
    "auth.master.manage_roles": "Manage authorization roles and role grants.",
    "auth.master.manage_scopes": "Manage the OAuth2 scope catalog.",
    "auth.internal.provision_human": "Provision a human authorization principal.",
    "auth.internal.set_principal_status": "Set human authorization principal status.",
    "auth.internal.assign_role": ("Assign a human authorization role from an internal service."),
    "auth.internal.issue_login_grant": "Issue a one-time human login grant.",
}

_ROLE_SCOPE_GRANTS = (
    ("user", "accounts.self.read", True),
    ("user", "accounts.self.update_nickname", True),
    ("support", "accounts.self.read", True),
    ("support", "accounts.self.update_nickname", True),
    ("support", "accounts.support.read", False),
    ("master", "accounts.self.read", True),
    ("master", "accounts.self.update_nickname", True),
    ("master", "accounts.support.read", False),
    ("master", "accounts.master.create_staff", False),
    ("master", "accounts.master.disable", False),
    ("master", "accounts.master.enable", False),
    ("master", "accounts.master.assign_role", False),
    ("master", "auth.master.manage_clients", False),
    ("master", "auth.master.manage_roles", False),
    ("master", "auth.master.manage_scopes", False),
)


def upgrade() -> None:
    """Create and seed the authorization foundation."""
    op.create_table(
        "authorization_roles",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("code", sa.String(length=16), nullable=False),
        sa.Column("principal_type", sa.String(length=16), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.CheckConstraint(
            "code IN ('user', 'support', 'master', 'auto')",
            name="ck_authorization_roles_code",
        ),
        sa.CheckConstraint(
            "principal_type IN ('human', 'service')",
            name="ck_authorization_roles_principal_type",
        ),
        sa.CheckConstraint(
            "(principal_type = 'human' AND code IN ('user', 'support', 'master')) "
            "OR (principal_type = 'service' AND code = 'auto')",
            name="ck_authorization_roles_code_principal_type",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_authorization_roles"),
        sa.UniqueConstraint("code", name="uq_authorization_roles_code"),
        sa.UniqueConstraint(
            "id",
            "principal_type",
            name="uq_authorization_roles_id_principal_type",
        ),
    )

    op.create_table(
        "oauth_scopes",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.CheckConstraint(
            "name ~ '^[a-z][a-z0-9_]*([.][a-z][a-z0-9_]*)+$'",
            name="ck_oauth_scopes_name_format",
        ),
        sa.CheckConstraint(
            "length(btrim(description)) > 0",
            name="ck_oauth_scopes_description_not_empty",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_oauth_scopes"),
        sa.UniqueConstraint("name", name="uq_oauth_scopes_name"),
    )

    op.create_table(
        "role_scope_grants",
        sa.Column("role_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("scope_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("is_default", sa.Boolean(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["role_id"],
            ["authorization_roles.id"],
            name="fk_role_scope_grants_role_id_authorization_roles",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["scope_id"],
            ["oauth_scopes.id"],
            name="fk_role_scope_grants_scope_id_oauth_scopes",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("role_id", "scope_id", name="pk_role_scope_grants"),
    )

    op.create_table(
        "authorization_principals",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("principal_type", sa.String(length=16), nullable=False),
        sa.Column("role_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.Column("account_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("service_slug", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.CheckConstraint(
            "principal_type IN ('human', 'service')",
            name="ck_authorization_principals_principal_type",
        ),
        sa.CheckConstraint(
            "status IN ('active', 'disabled')",
            name="ck_authorization_principals_status",
        ),
        sa.CheckConstraint(
            "(principal_type = 'human' AND account_id IS NOT NULL "
            "AND service_slug IS NULL) OR "
            "(principal_type = 'service' AND account_id IS NULL "
            "AND service_slug IS NOT NULL)",
            name="ck_authorization_principals_binding",
        ),
        sa.CheckConstraint(
            "service_slug IS NULL OR length(btrim(service_slug)) > 0",
            name="ck_authorization_principals_service_slug_not_empty",
        ),
        sa.ForeignKeyConstraint(
            ["role_id", "principal_type"],
            ["authorization_roles.id", "authorization_roles.principal_type"],
            name="fk_authorization_principals_role_id_authorization_roles",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_authorization_principals"),
        sa.UniqueConstraint(
            "account_id",
            name="uq_authorization_principals_account_id",
        ),
        sa.UniqueConstraint(
            "service_slug",
            name="uq_authorization_principals_service_slug",
        ),
    )

    roles = sa.table(
        "authorization_roles",
        sa.column("id", postgresql.UUID(as_uuid=True)),
        sa.column("code", sa.String(length=16)),
        sa.column("principal_type", sa.String(length=16)),
    )
    scopes = sa.table(
        "oauth_scopes",
        sa.column("id", postgresql.UUID(as_uuid=True)),
        sa.column("name", sa.Text()),
        sa.column("description", sa.Text()),
    )
    grants = sa.table(
        "role_scope_grants",
        sa.column("role_id", postgresql.UUID(as_uuid=True)),
        sa.column("scope_id", postgresql.UUID(as_uuid=True)),
        sa.column("is_default", sa.Boolean()),
    )

    op.bulk_insert(
        roles,
        [
            {"id": _ROLE_IDS["user"], "code": "user", "principal_type": "human"},
            {
                "id": _ROLE_IDS["support"],
                "code": "support",
                "principal_type": "human",
            },
            {"id": _ROLE_IDS["master"], "code": "master", "principal_type": "human"},
            {"id": _ROLE_IDS["auto"], "code": "auto", "principal_type": "service"},
        ],
    )
    op.bulk_insert(
        scopes,
        [
            {"id": _SCOPE_IDS[name], "name": name, "description": description}
            for name, description in _SCOPE_DESCRIPTIONS.items()
        ],
    )
    op.bulk_insert(
        grants,
        [
            {
                "role_id": _ROLE_IDS[role],
                "scope_id": _SCOPE_IDS[scope],
                "is_default": is_default,
            }
            for role, scope, is_default in _ROLE_SCOPE_GRANTS
        ],
    )


def downgrade() -> None:
    """Drop the authorization foundation and its canonical data."""
    op.drop_table("authorization_principals")
    op.drop_table("role_scope_grants")
    op.drop_table("oauth_scopes")
    op.drop_table("authorization_roles")
