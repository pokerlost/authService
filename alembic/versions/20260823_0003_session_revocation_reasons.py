"""Add AUTH-05 human session revocation reasons.

Revision ID: 20260823_0003
Revises: 20260823_0002
Create Date: 2026-08-23
"""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op

revision: str = "20260823_0003"
down_revision: str | Sequence[str] | None = "20260823_0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Permit logout and manual session revocation reasons."""
    op.drop_constraint(
        op.f("ck_sessions_revocation_reason"),
        "sessions",
        type_="check",
    )
    op.create_check_constraint(
        op.f("ck_sessions_revocation_reason"),
        "sessions",
        "revocation_reason IS NULL OR revocation_reason IN "
        "('refresh_reuse', 'principal_disabled', 'invalid_human_role', "
        "'logout', 'logout_all', 'manual')",
    )


def downgrade() -> None:
    """Restore the AUTH-04 session revocation-reason set."""
    op.drop_constraint(
        op.f("ck_sessions_revocation_reason"),
        "sessions",
        type_="check",
    )
    op.create_check_constraint(
        op.f("ck_sessions_revocation_reason"),
        "sessions",
        "revocation_reason IS NULL OR revocation_reason IN "
        "('refresh_reuse', 'principal_disabled', 'invalid_human_role')",
    )
