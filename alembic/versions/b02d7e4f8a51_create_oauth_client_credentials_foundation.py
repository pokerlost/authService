"""Migration: create OAuth2 client-credentials foundation.

Revision ID: b02d7e4f8a51
Revises: a01f6b2c9d34
Create Date: 2026-08-31
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "b02d7e4f8a51"
down_revision: str | Sequence[str] | None = "a01f6b2c9d34"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create OAuth2 clients and exact service/client authorization grants."""
    op.create_table(
        "oauth_clients",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("client_type", sa.String(length=16), nullable=False),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.Column(
            "bound_principal_id",
            postgresql.UUID(as_uuid=True),
            nullable=True,
        ),
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
            "client_type IN ('public', 'confidential')",
            name="ck_oauth_clients_client_type",
        ),
        sa.CheckConstraint(
            "status IN ('active', 'disabled')",
            name="ck_oauth_clients_status",
        ),
        sa.CheckConstraint(
            "(client_type = 'public' AND bound_principal_id IS NULL) OR "
            "(client_type = 'confidential' AND bound_principal_id IS NOT NULL)",
            name="ck_oauth_clients_binding",
        ),
        sa.ForeignKeyConstraint(
            ["bound_principal_id"],
            ["authorization_principals.id"],
            name="fk_oauth_clients_bound_principal_id_authorization_principals",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_oauth_clients"),
    )

    op.create_table(
        "oauth_client_grant_types",
        sa.Column("client_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("grant_type", sa.String(length=64), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.CheckConstraint(
            "grant_type IN ('client_credentials', 'refresh_token', "
            "'urn:pokerlost:params:oauth:grant-type:login-grant')",
            name="ck_oauth_client_grant_types_grant_type",
        ),
        sa.ForeignKeyConstraint(
            ["client_id"],
            ["oauth_clients.id"],
            name="fk_oauth_client_grant_types_client_id_oauth_clients",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint(
            "client_id",
            "grant_type",
            name="pk_oauth_client_grant_types",
        ),
    )

    op.create_table(
        "oauth_client_secrets",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("client_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("secret_digest", sa.LargeBinary(), nullable=False),
        sa.Column("status", sa.String(length=16), nullable=False),
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
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            "octet_length(secret_digest) = 32",
            name="ck_oauth_client_secrets_secret_digest_length",
        ),
        sa.CheckConstraint(
            "status IN ('active', 'retiring', 'revoked')",
            name="ck_oauth_client_secrets_status",
        ),
        sa.CheckConstraint(
            "updated_at >= created_at",
            name="ck_oauth_client_secrets_updated_at",
        ),
        sa.CheckConstraint(
            "expires_at IS NULL OR expires_at > created_at",
            name="ck_oauth_client_secrets_expires_at",
        ),
        sa.CheckConstraint(
            "revoked_at IS NULL OR revoked_at >= created_at",
            name="ck_oauth_client_secrets_revoked_at",
        ),
        sa.CheckConstraint(
            "(status IN ('active', 'retiring') AND revoked_at IS NULL) OR "
            "(status = 'revoked' AND revoked_at IS NOT NULL)",
            name="ck_oauth_client_secrets_state",
        ),
        sa.ForeignKeyConstraint(
            ["client_id"],
            ["oauth_clients.id"],
            name="fk_oauth_client_secrets_client_id_oauth_clients",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_oauth_client_secrets"),
        sa.UniqueConstraint(
            "secret_digest",
            name="uq_oauth_client_secrets_secret_digest",
        ),
    )
    op.create_index(
        "ix_oauth_client_secrets_client_id",
        "oauth_client_secrets",
        ["client_id"],
        unique=False,
    )

    op.create_table(
        "service_scope_grants",
        sa.Column("principal_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("scope_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["principal_id"],
            ["authorization_principals.id"],
            name="fk_service_scope_grants_principal_id_authorization_principals",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["scope_id"],
            ["oauth_scopes.id"],
            name="fk_service_scope_grants_scope_id_oauth_scopes",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint(
            "principal_id",
            "scope_id",
            name="pk_service_scope_grants",
        ),
    )

    op.create_table(
        "oauth_client_scope_grants",
        sa.Column("client_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("scope_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["client_id"],
            ["oauth_clients.id"],
            name="fk_oauth_client_scope_grants_client_id_oauth_clients",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["scope_id"],
            ["oauth_scopes.id"],
            name="fk_oauth_client_scope_grants_scope_id_oauth_scopes",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint(
            "client_id",
            "scope_id",
            name="pk_oauth_client_scope_grants",
        ),
    )

    op.create_table(
        "service_audience_grants",
        sa.Column("principal_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("audience", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.CheckConstraint(
            "audience ~ '^urn:pokerlost:service:[a-z][A-Za-z0-9]*$'",
            name="ck_service_audience_grants_audience_format",
        ),
        sa.ForeignKeyConstraint(
            ["principal_id"],
            ["authorization_principals.id"],
            name="fk_service_audience_grants_principal_authorization_principals",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint(
            "principal_id",
            "audience",
            name="pk_service_audience_grants",
        ),
    )

    op.create_table(
        "oauth_client_audience_grants",
        sa.Column("client_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("audience", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.CheckConstraint(
            "audience ~ '^urn:pokerlost:service:[a-z][A-Za-z0-9]*$'",
            name="ck_oauth_client_audience_grants_audience_format",
        ),
        sa.ForeignKeyConstraint(
            ["client_id"],
            ["oauth_clients.id"],
            name="fk_oauth_client_audience_grants_client_id_oauth_clients",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint(
            "client_id",
            "audience",
            name="pk_oauth_client_audience_grants",
        ),
    )


def downgrade() -> None:
    """Drop only the OAuth2 client-credentials foundation."""
    op.drop_table("oauth_client_audience_grants")
    op.drop_table("service_audience_grants")
    op.drop_table("oauth_client_scope_grants")
    op.drop_table("service_scope_grants")
    op.drop_table("oauth_client_secrets")
    op.drop_table("oauth_client_grant_types")
    op.drop_table("oauth_clients")
