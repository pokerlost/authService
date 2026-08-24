"""Create the OpenAPI authorization registry and ownership ledger.

Revision ID: 20260823_0005
Revises: 20260823_0004
Create Date: 2026-08-23
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260823_0005"
down_revision: str | Sequence[str] | None = "20260823_0004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create immutable contracts, normalized policies, and permanent operation ownership."""
    op.create_table(
        "registered_services",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("service_id", sa.String(length=63), nullable=False),
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
            "char_length(service_id) BETWEEN 2 AND 63",
            name=op.f("ck_registered_services_service_id_length"),
        ),
        sa.CheckConstraint(
            "service_id ~ '^[a-z][A-Za-z0-9]{1,62}$'",
            name=op.f("ck_registered_services_service_id_format"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_registered_services")),
        sa.UniqueConstraint(
            "service_id",
            name=op.f("uq_registered_services_service_id"),
        ),
    )
    op.create_table(
        "openapi_contracts",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("registered_service_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("contract_version", sa.String(length=64), nullable=False),
        sa.Column("openapi_version", sa.String(length=16), nullable=False),
        sa.Column("schema_hash", sa.String(length=64), nullable=False),
        sa.Column(
            "document",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
        ),
        sa.Column("status", sa.String(length=10), nullable=False),
        sa.Column("validated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("activated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("retired_at", sa.DateTime(timezone=True), nullable=True),
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
            "char_length(contract_version) BETWEEN 1 AND 64",
            name=op.f("ck_openapi_contracts_contract_version_length"),
        ),
        sa.CheckConstraint(
            "char_length(openapi_version) BETWEEN 1 AND 16",
            name=op.f("ck_openapi_contracts_openapi_version_length"),
        ),
        sa.CheckConstraint(
            "schema_hash ~ '^[0-9a-f]{64}$'",
            name=op.f("ck_openapi_contracts_schema_hash_format"),
        ),
        sa.CheckConstraint(
            "status IN ('registered', 'validated', 'active', 'retired')",
            name=op.f("ck_openapi_contracts_status"),
        ),
        sa.CheckConstraint(
            "(status = 'registered' AND validated_at IS NULL AND activated_at IS NULL "
            "AND retired_at IS NULL) OR "
            "(status = 'validated' AND validated_at IS NOT NULL AND activated_at IS NULL "
            "AND retired_at IS NULL) OR "
            "(status = 'active' AND validated_at IS NOT NULL AND activated_at IS NOT NULL "
            "AND retired_at IS NULL) OR "
            "(status = 'retired' AND validated_at IS NOT NULL AND retired_at IS NOT NULL)",
            name=op.f("ck_openapi_contracts_lifecycle"),
        ),
        sa.ForeignKeyConstraint(
            ["registered_service_id"],
            ["registered_services.id"],
            name=op.f("fk_openapi_contracts_registered_service_id_registered_services"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_openapi_contracts")),
        sa.UniqueConstraint(
            "registered_service_id",
            "contract_version",
            name=op.f("uq_openapi_contracts_service_version"),
        ),
        sa.UniqueConstraint(
            "registered_service_id",
            "schema_hash",
            name=op.f("uq_openapi_contracts_service_schema_hash"),
        ),
    )
    op.create_index(
        "uq_openapi_contracts_one_active_service",
        "openapi_contracts",
        ["registered_service_id"],
        unique=True,
        postgresql_where=sa.text("status = 'active'"),
    )
    op.create_table(
        "operation_identities",
        sa.Column("api_operation_id", sa.String(length=255), nullable=False),
        sa.Column("registered_service_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "claimed_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "char_length(api_operation_id) BETWEEN 3 AND 255",
            name=op.f("ck_operation_identities_api_operation_id_length"),
        ),
        sa.CheckConstraint(
            "api_operation_id ~ '^[a-z][A-Za-z0-9]{1,62}(\\.[a-z][A-Za-z0-9]{0,62}){1,2}$'",
            name=op.f("ck_operation_identities_api_operation_id_format"),
        ),
        sa.ForeignKeyConstraint(
            ["registered_service_id"],
            ["registered_services.id"],
            name=op.f("fk_operation_identities_registered_service_id_registered_services"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("api_operation_id", name=op.f("pk_operation_identities")),
    )
    op.create_table(
        "api_operations",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("contract_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("api_operation_id", sa.String(length=255), nullable=False),
        sa.Column("http_method", sa.String(length=4), nullable=False),
        sa.Column("path", sa.String(length=255), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "char_length(api_operation_id) BETWEEN 3 AND 255",
            name=op.f("ck_api_operations_api_operation_id_length"),
        ),
        sa.CheckConstraint(
            "api_operation_id ~ '^[a-z][A-Za-z0-9]{1,62}(\\.[a-z][A-Za-z0-9]{0,62}){1,2}$'",
            name=op.f("ck_api_operations_api_operation_id_format"),
        ),
        sa.CheckConstraint(
            "http_method IN ('GET', 'POST')",
            name=op.f("ck_api_operations_http_method"),
        ),
        sa.CheckConstraint(
            "char_length(path) BETWEEN 1 AND 255 AND left(path, 1) = '/'",
            name=op.f("ck_api_operations_path"),
        ),
        sa.ForeignKeyConstraint(
            ["contract_id"],
            ["openapi_contracts.id"],
            name=op.f("fk_api_operations_contract_id_openapi_contracts"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_api_operations")),
        sa.UniqueConstraint(
            "contract_id",
            "api_operation_id",
            name=op.f("uq_api_operations_contract_operation_id"),
        ),
        sa.UniqueConstraint(
            "contract_id",
            "http_method",
            "path",
            name=op.f("uq_api_operations_contract_method_path"),
        ),
    )
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
        sa.PrimaryKeyConstraint("api_operation_id", name=op.f("pk_authorization_policies")),
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


def downgrade() -> None:
    """Drop normalized registry state while leaving AUTH-04 through AUTH-07 intact."""
    op.drop_table("authorization_policy_roles")
    op.drop_table("authorization_policies")
    op.drop_table("api_operations")
    op.drop_table("operation_identities")
    op.drop_index(
        "uq_openapi_contracts_one_active_service",
        table_name="openapi_contracts",
        postgresql_where=sa.text("status = 'active'"),
    )
    op.drop_table("openapi_contracts")
    op.drop_table("registered_services")
