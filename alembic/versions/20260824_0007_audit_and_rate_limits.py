"""Create durable security audit and PostgreSQL authentication rate limits.

Revision ID: 20260824_0007
Revises: 20260824_0006
Create Date: 2026-08-24
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260824_0007"
down_revision: str | Sequence[str] | None = "20260824_0006"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_AUDIT_EVENT_TYPES = (
    "user_registered",
    "password_grant_succeeded",
    "password_grant_failed",
    "client_credentials_succeeded",
    "client_credentials_failed",
    "oauth_token_refreshed",
    "oauth_refresh_reuse_detected",
    "session_revoked",
    "all_sessions_revoked",
    "password_changed",
    "password_reset_by_master",
    "support_account_created",
    "master_account_created",
    "account_disabled",
    "account_enabled",
    "service_principal_created",
    "service_credential_created",
    "service_credential_revoked",
    "service_audience_granted",
    "service_audience_revoked",
    "service_scope_granted",
    "service_scope_revoked",
    "role_scope_granted",
    "role_scope_revoked",
    "openapi_contract_registered",
    "openapi_contract_validated",
    "openapi_contract_activation_succeeded",
    "openapi_contract_activation_failed",
    "openapi_contract_retired",
)


def upgrade() -> None:
    """Create append-only audit events and multi-instance limiter rows."""
    op.drop_index("ix_sessions_principal_id", table_name="sessions")
    op.create_index(
        "ix_sessions_principal_id_status",
        "sessions",
        ["principal_id", "status"],
        unique=False,
    )

    event_types = ", ".join(f"'{event_type}'" for event_type in _AUDIT_EVENT_TYPES)
    op.create_table(
        "audit_events",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column(
            "occurred_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("event_type", sa.String(length=64), nullable=False),
        sa.Column("result", sa.String(length=7), nullable=False),
        sa.Column("actor_principal_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("actor_role", sa.String(length=7), nullable=True),
        sa.Column("target_type", sa.String(length=64), nullable=True),
        sa.Column("target_id", sa.String(length=255), nullable=True),
        sa.Column("request_id", sa.String(length=128), nullable=True),
        sa.Column("correlation_id", sa.String(length=128), nullable=True),
        sa.Column("api_operation_id", sa.String(length=255), nullable=True),
        sa.Column(
            "metadata",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.CheckConstraint(
            f"event_type IN ({event_types})",
            name=op.f("ck_audit_events_event_type"),
        ),
        sa.CheckConstraint(
            "result IN ('success', 'failure')",
            name=op.f("ck_audit_events_result"),
        ),
        sa.CheckConstraint(
            "actor_role IS NULL OR actor_role IN ('user', 'support', 'master', 'auto')",
            name=op.f("ck_audit_events_actor_role"),
        ),
        sa.CheckConstraint(
            "jsonb_typeof(metadata) = 'object'",
            name=op.f("ck_audit_events_metadata_object"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_audit_events")),
    )
    op.create_index(
        "ix_audit_events_occurred_at_id",
        "audit_events",
        ["occurred_at", "id"],
        unique=False,
    )
    op.create_index(
        "ix_audit_events_event_type_occurred_at",
        "audit_events",
        ["event_type", "occurred_at"],
        unique=False,
    )

    op.create_table(
        "security_rate_limits",
        sa.Column("kind", sa.String(length=18), nullable=False),
        sa.Column("key_fingerprint", sa.String(length=64), nullable=False),
        sa.Column("window_started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("attempt_count", sa.Integer(), nullable=False),
        sa.Column("locked_until", sa.DateTime(timezone=True), nullable=True),
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
            "kind IN ('password', 'client_credentials')",
            name=op.f("ck_security_rate_limits_kind"),
        ),
        sa.CheckConstraint(
            "key_fingerprint ~ '^[0-9a-f]{64}$'",
            name=op.f("ck_security_rate_limits_key_fingerprint"),
        ),
        sa.CheckConstraint(
            "attempt_count >= 0",
            name=op.f("ck_security_rate_limits_attempt_count"),
        ),
        sa.PrimaryKeyConstraint(
            "kind",
            "key_fingerprint",
            name=op.f("pk_security_rate_limits"),
        ),
    )
    op.create_index(
        "ix_security_rate_limits_updated_at",
        "security_rate_limits",
        ["updated_at"],
        unique=False,
    )


def downgrade() -> None:
    """Drop AUTH-09 limiter and audit storage."""
    op.drop_index(
        "ix_security_rate_limits_updated_at",
        table_name="security_rate_limits",
    )
    op.drop_table("security_rate_limits")
    op.drop_index(
        "ix_audit_events_event_type_occurred_at",
        table_name="audit_events",
    )
    op.drop_index("ix_audit_events_occurred_at_id", table_name="audit_events")
    op.drop_table("audit_events")
    op.drop_index("ix_sessions_principal_id_status", table_name="sessions")
    op.create_index(
        "ix_sessions_principal_id",
        "sessions",
        ["principal_id"],
        unique=False,
    )
