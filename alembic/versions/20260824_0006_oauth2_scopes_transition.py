"""Transition runtime and registry authorization to canonical OAuth2 scopes.

Revision ID: 20260824_0006
Revises: 20260823_0005
Create Date: 2026-08-24

The upgrade intentionally retires legacy normalized contracts and revokes all
pre-scope human sessions. Downgrade restores the old schema shape but does not
resurrect retired contracts or revoked authentication state.
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260824_0006"
down_revision: str | Sequence[str] | None = "20260823_0005"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_HUMAN_SESSION_SCOPES = (
    "authService.account.changePassword",
    "authService.auth.logout",
    "authService.auth.logoutAll",
    "authService.sessions.list",
    "authService.sessions.revoke",
)
_SUPPORT_SCOPES = ("authService.support.getUserAccount",)
_MASTER_SCOPES = (
    "authService.master.activateOpenApiContract",
    "authService.master.createAutoPrincipal",
    "authService.master.createMasterAccount",
    "authService.master.createServiceCredential",
    "authService.master.createSupportAccount",
    "authService.master.diffOpenApiContract",
    "authService.master.disableAccount",
    "authService.master.enableAccount",
    "authService.master.getAuthorizationManifest",
    "authService.master.getOpenApiContract",
    "authService.master.getRegisteredService",
    "authService.master.grantRoleScope",
    "authService.master.grantServiceAudience",
    "authService.master.grantServiceScope",
    "authService.master.listAuditEvents",
    "authService.master.listOpenApiContracts",
    "authService.master.listRegisteredServices",
    "authService.master.listRoleScopes",
    "authService.master.listServiceScopes",
    "authService.master.registerOpenApiContract",
    "authService.master.resetHumanPassword",
    "authService.master.retireOpenApiContract",
    "authService.master.revokeRoleScope",
    "authService.master.revokeServiceAudience",
    "authService.master.revokeServiceCredential",
    "authService.master.revokeServiceScope",
    "authService.master.validateOpenApiContract",
)
_PUBLIC_OPERATIONS = (
    "authService.jwks.get",
    "authService.oauth.token",
    "authService.openapi.get",
    "authService.root",
    "authService.users.register",
)
_ALL_OPERATIONS = (
    *_PUBLIC_OPERATIONS,
    *_HUMAN_SESSION_SCOPES,
    *_SUPPORT_SCOPES,
    *_MASTER_SCOPES,
)


def _values(values: tuple[str, ...]) -> str:
    """Render trusted static values for PostgreSQL VALUES clauses."""
    return ", ".join(f"('{value}')" for value in values)


def _role_grant_values() -> str:
    """Render the explicit no-inheritance authService role grant seed."""
    grants = [
        *(
            (role, scope)
            for role in ("user", "support", "master")
            for scope in _HUMAN_SESSION_SCOPES
        ),
        *((role, scope) for role in ("support", "master") for scope in _SUPPORT_SCOPES),
        *(("master", scope) for scope in _MASTER_SCOPES),
    ]
    return ", ".join(f"('{role}', '{scope}')" for role, scope in grants)


def upgrade() -> None:
    """Install scope grants, session ceilings, and scope-only registry authorization."""
    op.drop_constraint(op.f("ck_sessions_revocation_reason"), "sessions", type_="check")
    op.create_check_constraint(
        op.f("ck_sessions_revocation_reason"),
        "sessions",
        "revocation_reason IS NULL OR revocation_reason IN "
        "('refresh_reuse', 'principal_disabled', 'invalid_human_role', "
        "'logout', 'logout_all', 'manual', 'password_changed', "
        "'password_reset', 'oauth2_migration')",
    )

    op.execute(
        sa.text(
            "UPDATE sessions SET status = 'revoked', revoked_at = now(), "
            "revocation_reason = 'oauth2_migration', updated_at = now() "
            "WHERE status = 'active'"
        )
    )
    op.execute(
        sa.text(
            "UPDATE refresh_tokens SET revoked_at = COALESCE(revoked_at, now()) "
            "WHERE revoked_at IS NULL"
        )
    )
    op.execute(
        sa.text(
            "UPDATE openapi_contracts SET status = 'retired', retired_at = now(), "
            "updated_at = now() WHERE status IN ('validated', 'active')"
        )
    )
    op.execute(sa.text("DELETE FROM api_operations"))
    op.drop_table("authorization_policy_roles")
    op.drop_table("authorization_policies")

    op.add_column(
        "api_operations",
        sa.Column("authorization_mode", sa.String(length=6), nullable=False),
    )
    op.add_column(
        "api_operations",
        sa.Column("required_scope", sa.String(length=255), nullable=True),
    )
    op.create_check_constraint(
        op.f("ck_api_operations_authorization_mode"),
        "api_operations",
        "authorization_mode IN ('public', 'oauth2')",
    )
    op.create_check_constraint(
        op.f("ck_api_operations_authorization_variant"),
        "api_operations",
        "(authorization_mode = 'public' AND required_scope IS NULL) OR "
        "(authorization_mode = 'oauth2' AND required_scope = api_operation_id)",
    )

    op.create_table(
        "role_scope_grants",
        sa.Column("role", sa.String(length=7), nullable=False),
        sa.Column("api_operation_id", sa.String(length=255), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "role IN ('user', 'support', 'master')",
            name=op.f("ck_role_scope_grants_human_role"),
        ),
        sa.ForeignKeyConstraint(
            ["api_operation_id"],
            ["operation_identities.api_operation_id"],
            name=op.f("fk_role_scope_grants_api_operation_id_operation_identities"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint(
            "role",
            "api_operation_id",
            name=op.f("pk_role_scope_grants"),
        ),
    )
    op.create_table(
        "service_scope_grants",
        sa.Column(
            "service_principal_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column("audience", sa.String(length=63), nullable=False),
        sa.Column("api_operation_id", sa.String(length=255), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "char_length(audience) BETWEEN 2 AND 63",
            name=op.f("ck_service_scope_grants_audience_length"),
        ),
        sa.CheckConstraint(
            "audience = lower(audience) AND audience ~ '^[a-z0-9-]+$'",
            name=op.f("ck_service_scope_grants_audience_format"),
        ),
        sa.ForeignKeyConstraint(
            ["api_operation_id"],
            ["operation_identities.api_operation_id"],
            name=op.f("fk_service_scope_grants_api_operation_id_operation_identities"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["service_principal_id"],
            ["service_principals.principal_id"],
            name=op.f("fk_service_scope_grants_service_principal_id_service_principals"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint(
            "service_principal_id",
            "audience",
            "api_operation_id",
            name=op.f("pk_service_scope_grants"),
        ),
    )
    op.create_table(
        "session_scopes",
        sa.Column("session_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("api_operation_id", sa.String(length=255), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["api_operation_id"],
            ["operation_identities.api_operation_id"],
            name=op.f("fk_session_scopes_api_operation_id_operation_identities"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["session_id"],
            ["sessions.id"],
            name=op.f("fk_session_scopes_session_id_sessions"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint(
            "session_id",
            "api_operation_id",
            name=op.f("pk_session_scopes"),
        ),
    )

    op.execute(
        sa.text(
            "INSERT INTO registered_services (id, service_id) "
            "VALUES (gen_random_uuid(), 'authService') "
            "ON CONFLICT (service_id) DO NOTHING"
        )
    )
    operation_values = _values(_ALL_OPERATIONS)
    op.execute(
        sa.text(
            "DO $$ BEGIN "
            "IF EXISTS ("
            "SELECT 1 FROM operation_identities oi "
            "JOIN registered_services rs ON rs.id = oi.registered_service_id "
            f"WHERE oi.api_operation_id IN (SELECT value FROM (VALUES {operation_values}) "
            "AS requested(value)) AND rs.service_id <> 'authService'"
            ") THEN RAISE EXCEPTION "
            "'An authService operationId is owned by another registered service'; "
            "END IF; END $$"
        )
    )
    op.execute(
        sa.text(
            "INSERT INTO operation_identities (api_operation_id, registered_service_id) "
            "SELECT requested.value, rs.id "
            f"FROM (VALUES {operation_values}) AS requested(value) "
            "JOIN registered_services rs ON rs.service_id = 'authService' "
            "ON CONFLICT (api_operation_id) DO NOTHING"
        )
    )
    op.execute(
        sa.text(
            "INSERT INTO role_scope_grants (role, api_operation_id) "
            f"VALUES {_role_grant_values()} "
            "ON CONFLICT (role, api_operation_id) DO NOTHING"
        )
    )


def downgrade() -> None:
    """Restore the pre-scope schema without resurrecting invalidated runtime state."""
    op.drop_table("session_scopes")
    op.drop_table("service_scope_grants")
    op.drop_table("role_scope_grants")

    op.execute(
        sa.text(
            "UPDATE openapi_contracts SET status = 'retired', "
            "retired_at = COALESCE(retired_at, now()), updated_at = now() "
            "WHERE status IN ('validated', 'active')"
        )
    )
    op.execute(sa.text("DELETE FROM api_operations"))
    op.drop_constraint(
        op.f("ck_api_operations_authorization_variant"),
        "api_operations",
        type_="check",
    )
    op.drop_constraint(
        op.f("ck_api_operations_authorization_mode"),
        "api_operations",
        type_="check",
    )
    op.drop_column("api_operations", "required_scope")
    op.drop_column("api_operations", "authorization_mode")

    op.create_table(
        "authorization_policies",
        sa.Column("api_operation_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("mode", sa.String(length=10), nullable=False),
        sa.Column("credential_type", sa.String(length=7), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "mode IN ('public', 'roles', 'credential')",
            name=op.f("ck_authorization_policies_mode"),
        ),
        sa.CheckConstraint(
            "credential_type IS NULL OR credential_type IN ('refresh', 'service')",
            name=op.f("ck_authorization_policies_credential_type"),
        ),
        sa.CheckConstraint(
            "(mode IN ('public', 'roles') AND credential_type IS NULL) OR "
            "(mode = 'credential' AND credential_type IS NOT NULL)",
            name=op.f("ck_authorization_policies_variant"),
        ),
        sa.ForeignKeyConstraint(
            ["api_operation_id"],
            ["api_operations.id"],
            name=op.f("fk_authorization_policies_api_operation_id_api_operations"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint(
            "api_operation_id",
            name=op.f("pk_authorization_policies"),
        ),
    )
    op.create_table(
        "authorization_policy_roles",
        sa.Column("api_operation_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("role", sa.String(length=7), nullable=False),
        sa.CheckConstraint(
            "role IN ('user', 'support', 'master', 'auto')",
            name=op.f("ck_authorization_policy_roles_role"),
        ),
        sa.ForeignKeyConstraint(
            ["api_operation_id"],
            ["authorization_policies.api_operation_id"],
            name=op.f("fk_authorization_policy_roles_api_operation_id_authorization_policies"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint(
            "api_operation_id",
            "role",
            name=op.f("pk_authorization_policy_roles"),
        ),
    )

    op.execute(
        sa.text(
            "UPDATE sessions SET revocation_reason = 'manual', updated_at = now() "
            "WHERE revocation_reason IN "
            "('password_changed', 'password_reset', 'oauth2_migration')"
        )
    )
    op.drop_constraint(op.f("ck_sessions_revocation_reason"), "sessions", type_="check")
    op.create_check_constraint(
        op.f("ck_sessions_revocation_reason"),
        "sessions",
        "revocation_reason IS NULL OR revocation_reason IN "
        "('refresh_reuse', 'principal_disabled', 'invalid_human_role', "
        "'logout', 'logout_all', 'manual')",
    )
