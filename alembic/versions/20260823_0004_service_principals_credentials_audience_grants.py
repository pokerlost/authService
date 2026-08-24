"""Create AUTO service principals, credentials, and audience grants.

Revision ID: 20260823_0004
Revises: 20260823_0003
Create Date: 2026-08-23
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260823_0004"
down_revision: str | Sequence[str] | None = "20260823_0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create AUTH-06 digest-only service authentication storage."""
    op.create_table(
        "service_principals",
        sa.Column("principal_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("service_slug", sa.String(length=63), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "char_length(service_slug) BETWEEN 2 AND 63",
            name=op.f("ck_service_principals_service_slug_length"),
        ),
        sa.CheckConstraint(
            "service_slug = lower(service_slug)",
            name=op.f("ck_service_principals_service_slug_lowercase"),
        ),
        sa.CheckConstraint(
            "service_slug ~ '^[a-z0-9-]+$'",
            name=op.f("ck_service_principals_service_slug_format"),
        ),
        sa.ForeignKeyConstraint(
            ["principal_id"],
            ["principals.id"],
            name=op.f("fk_service_principals_principal_id_principals"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("principal_id", name=op.f("pk_service_principals")),
        sa.UniqueConstraint(
            "service_slug",
            name=op.f("uq_service_principals_service_slug"),
        ),
    )
    op.create_table(
        "service_credentials",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("service_principal_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("client_id", sa.String(length=64), nullable=False),
        sa.Column("secret_digest", sa.LargeBinary(length=32), nullable=False),
        sa.Column("status", sa.String(length=7), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "char_length(client_id) BETWEEN 16 AND 64",
            name=op.f("ck_service_credentials_client_id_length"),
        ),
        sa.CheckConstraint(
            "client_id ~ '^[A-Za-z0-9_-]+$'",
            name=op.f("ck_service_credentials_client_id_format"),
        ),
        sa.CheckConstraint(
            "octet_length(secret_digest) = 32",
            name=op.f("ck_service_credentials_secret_digest_length"),
        ),
        sa.CheckConstraint(
            "status IN ('active', 'revoked')",
            name=op.f("ck_service_credentials_status"),
        ),
        sa.CheckConstraint(
            "expires_at > created_at",
            name=op.f("ck_service_credentials_expiration"),
        ),
        sa.CheckConstraint(
            "(status = 'active' AND revoked_at IS NULL) OR "
            "(status = 'revoked' AND revoked_at IS NOT NULL)",
            name=op.f("ck_service_credentials_revocation_state"),
        ),
        sa.ForeignKeyConstraint(
            ["service_principal_id"],
            ["service_principals.principal_id"],
            name=op.f("fk_service_credentials_service_principal_id_service_principals"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_service_credentials")),
        sa.UniqueConstraint(
            "client_id",
            name=op.f("uq_service_credentials_client_id"),
        ),
    )
    op.create_index(
        "ix_service_credentials_service_principal_id",
        "service_credentials",
        ["service_principal_id"],
        unique=False,
    )
    op.create_table(
        "service_audience_grants",
        sa.Column("service_principal_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("audience", sa.String(length=63), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "char_length(audience) BETWEEN 2 AND 63",
            name=op.f("ck_service_audience_grants_audience_length"),
        ),
        sa.CheckConstraint(
            "audience = lower(audience)",
            name=op.f("ck_service_audience_grants_audience_lowercase"),
        ),
        sa.CheckConstraint(
            "audience ~ '^[a-z0-9-]+$'",
            name=op.f("ck_service_audience_grants_audience_format"),
        ),
        sa.ForeignKeyConstraint(
            ["service_principal_id"],
            ["service_principals.principal_id"],
            name=op.f("fk_service_audience_grants_service_principal_id_service_principals"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint(
            "service_principal_id",
            "audience",
            name=op.f("pk_service_audience_grants"),
        ),
    )


def downgrade() -> None:
    """Drop AUTH-06 audience grants, credentials, and service principals."""
    op.drop_table("service_audience_grants")
    op.drop_index(
        "ix_service_credentials_service_principal_id",
        table_name="service_credentials",
    )
    op.drop_table("service_credentials")
    op.drop_table("service_principals")
