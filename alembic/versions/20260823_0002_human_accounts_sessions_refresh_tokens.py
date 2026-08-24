"""Create human accounts, sessions, and refresh-token chains.

Revision ID: 20260823_0002
Revises: 20260822_0001
Create Date: 2026-08-23
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260823_0002"
down_revision: str | Sequence[str] | None = "20260822_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create AUTH-04 human account and session-family storage."""
    op.create_table(
        "human_accounts",
        sa.Column("principal_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("username", sa.String(length=32), nullable=False),
        sa.Column("nickname", sa.String(length=64), nullable=False),
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
            "username = lower(username)",
            name=op.f("ck_human_accounts_username_lowercase"),
        ),
        sa.CheckConstraint(
            "char_length(username) BETWEEN 3 AND 32",
            name=op.f("ck_human_accounts_username_length"),
        ),
        sa.CheckConstraint(
            "username ~ '^[a-z0-9_]+$'",
            name=op.f("ck_human_accounts_username_format"),
        ),
        sa.CheckConstraint(
            "nickname = btrim(nickname) AND char_length(nickname) BETWEEN 1 AND 64",
            name=op.f("ck_human_accounts_nickname"),
        ),
        sa.ForeignKeyConstraint(
            ["principal_id"],
            ["principals.id"],
            name=op.f("fk_human_accounts_principal_id_principals"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("principal_id", name=op.f("pk_human_accounts")),
        sa.UniqueConstraint("username", name=op.f("uq_human_accounts_username")),
    )
    op.create_table(
        "sessions",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("principal_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("status", sa.String(length=7), nullable=False),
        sa.Column("last_refreshed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("idle_expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("absolute_expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("revocation_reason", sa.String(length=24), nullable=True),
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
            "status IN ('active', 'revoked')",
            name=op.f("ck_sessions_status"),
        ),
        sa.CheckConstraint(
            "revocation_reason IS NULL OR revocation_reason IN "
            "('refresh_reuse', 'principal_disabled', 'invalid_human_role')",
            name=op.f("ck_sessions_revocation_reason"),
        ),
        sa.CheckConstraint(
            "idle_expires_at <= absolute_expires_at",
            name=op.f("ck_sessions_expiration_order"),
        ),
        sa.CheckConstraint(
            "(status = 'active' AND revoked_at IS NULL AND revocation_reason IS NULL) OR "
            "(status = 'revoked' AND revoked_at IS NOT NULL AND revocation_reason IS NOT NULL)",
            name=op.f("ck_sessions_revocation_state"),
        ),
        sa.ForeignKeyConstraint(
            ["principal_id"],
            ["principals.id"],
            name=op.f("fk_sessions_principal_id_principals"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_sessions")),
    )
    op.create_index("ix_sessions_principal_id", "sessions", ["principal_id"], unique=False)
    op.create_table(
        "refresh_tokens",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("session_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("lookup_id", sa.String(length=32), nullable=False),
        sa.Column("secret_digest", sa.LargeBinary(length=32), nullable=False),
        sa.Column("parent_token_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("replaced_by_token_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("consumed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("reuse_detected_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "char_length(lookup_id) = 22 AND lookup_id ~ '^[A-Za-z0-9_-]+$'",
            name=op.f("ck_refresh_tokens_lookup_id"),
        ),
        sa.CheckConstraint(
            "octet_length(secret_digest) = 32",
            name=op.f("ck_refresh_tokens_secret_digest_length"),
        ),
        sa.CheckConstraint(
            "parent_token_id IS NULL OR parent_token_id <> id",
            name=op.f("ck_refresh_tokens_parent_not_self"),
        ),
        sa.CheckConstraint(
            "replaced_by_token_id IS NULL OR replaced_by_token_id <> id",
            name=op.f("ck_refresh_tokens_replacement_not_self"),
        ),
        sa.CheckConstraint(
            "(consumed_at IS NULL AND replaced_by_token_id IS NULL) OR "
            "(consumed_at IS NOT NULL AND replaced_by_token_id IS NOT NULL)",
            name=op.f("ck_refresh_tokens_consumption_link"),
        ),
        sa.CheckConstraint(
            "reuse_detected_at IS NULL OR consumed_at IS NOT NULL",
            name=op.f("ck_refresh_tokens_reuse_after_consumption"),
        ),
        sa.ForeignKeyConstraint(
            ["parent_token_id"],
            ["refresh_tokens.id"],
            name=op.f("fk_refresh_tokens_parent_token_id_refresh_tokens"),
        ),
        sa.ForeignKeyConstraint(
            ["replaced_by_token_id"],
            ["refresh_tokens.id"],
            name=op.f("fk_refresh_tokens_replaced_by_token_id_refresh_tokens"),
        ),
        sa.ForeignKeyConstraint(
            ["session_id"],
            ["sessions.id"],
            name=op.f("fk_refresh_tokens_session_id_sessions"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_refresh_tokens")),
        sa.UniqueConstraint("lookup_id", name=op.f("uq_refresh_tokens_lookup_id")),
        sa.UniqueConstraint(
            "parent_token_id",
            name=op.f("uq_refresh_tokens_parent_token_id"),
        ),
        sa.UniqueConstraint(
            "replaced_by_token_id",
            name=op.f("uq_refresh_tokens_replaced_by_token_id"),
        ),
    )
    op.create_index(
        "ix_refresh_tokens_session_id",
        "refresh_tokens",
        ["session_id"],
        unique=False,
    )


def downgrade() -> None:
    """Drop AUTH-04 refresh-token, session, and human account storage."""
    op.drop_index("ix_refresh_tokens_session_id", table_name="refresh_tokens")
    op.drop_table("refresh_tokens")
    op.drop_index("ix_sessions_principal_id", table_name="sessions")
    op.drop_table("sessions")
    op.drop_table("human_accounts")
