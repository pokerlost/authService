"""Create principal and password credential storage.

Revision ID: 20260822_0001
Revises:
Create Date: 2026-08-22
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260822_0001"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create principal and password credential tables."""
    op.create_table(
        "principals",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("role", sa.String(length=7), nullable=False),
        sa.Column("status", sa.String(length=8), nullable=False),
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
            "role IN ('user', 'support', 'master', 'auto')",
            name=op.f("ck_principals_role"),
        ),
        sa.CheckConstraint(
            "status IN ('active', 'disabled')",
            name=op.f("ck_principals_status"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_principals")),
    )
    op.create_index(
        "ix_principals_role_status",
        "principals",
        ["role", "status"],
        unique=False,
    )
    op.create_table(
        "password_credentials",
        sa.Column(
            "principal_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column("password_hash", sa.Text(), nullable=False),
        sa.Column(
            "password_changed_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
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
        sa.ForeignKeyConstraint(
            ["principal_id"],
            ["principals.id"],
            name=op.f("fk_password_credentials_principal_id_principals"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint(
            "principal_id",
            name=op.f("pk_password_credentials"),
        ),
    )


def downgrade() -> None:
    """Drop principal and password credential tables."""
    op.drop_table("password_credentials")
    op.drop_index("ix_principals_role_status", table_name="principals")
    op.drop_table("principals")
