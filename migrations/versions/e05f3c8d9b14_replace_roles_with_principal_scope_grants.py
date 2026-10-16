"""Replace authorization roles with exact principal scope grants.

Revision ID: e05f3c8d9b14
Revises: d04e2b7c8a93
Create Date: 2026-09-03
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Sequence
from uuid import UUID

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql
from sqlalchemy.engine import Connection

revision: str = "e05f3c8d9b14"
down_revision: str | Sequence[str] | None = "d04e2b7c8a93"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_ROLE_IDS = {
    "user": UUID("10000000-0000-4000-8000-000000000001"),
    "support": UUID("10000000-0000-4000-8000-000000000002"),
    "master": UUID("10000000-0000-4000-8000-000000000003"),
    "auto": UUID("10000000-0000-4000-8000-000000000004"),
}

_SCOPE_IDS = {
    "accounts.self.getMe": UUID("20000000-0000-4000-8000-000000000001"),
    "accounts.self.updateNickname": UUID("20000000-0000-4000-8000-000000000002"),
    "accounts.account.read": UUID("20000000-0000-4000-8000-000000000003"),
    "accounts.staff.create": UUID("20000000-0000-4000-8000-000000000004"),
    "accounts.account.disable": UUID("20000000-0000-4000-8000-000000000005"),
    "accounts.account.enable": UUID("20000000-0000-4000-8000-000000000006"),
    "accounts.account.replaceScopes": UUID("20000000-0000-4000-8000-000000000007"),
    "auth.client.manage": UUID("20000000-0000-4000-8000-000000000008"),
    "auth.principal.replaceScopes": UUID("20000000-0000-4000-8000-000000000009"),
    "auth.scope.manage": UUID("20000000-0000-4000-8000-000000000010"),
    "auth.internal.provisionHuman": UUID("20000000-0000-4000-8000-000000000011"),
    "auth.internal.setPrincipalStatus": UUID("20000000-0000-4000-8000-000000000012"),
    "auth.internal.replacePrincipalScopes": UUID("20000000-0000-4000-8000-000000000013"),
    "auth.internal.issueLoginGrant": UUID("20000000-0000-4000-8000-000000000014"),
}

# previous name -> (current name, previous description, current description)
_SCOPE_CHANGES = {
    "accounts.self.read": (
        "accounts.self.getMe",
        "Read the current human account.",
        "Read the current human account.",
    ),
    "accounts.support.read": (
        "accounts.account.read",
        "Read support-safe account information.",
        "Read an account with an explicit account-read capability.",
    ),
    "accounts.master.createStaff": (
        "accounts.staff.create",
        "Create a staff account.",
        "Create a staff account.",
    ),
    "accounts.master.disable": (
        "accounts.account.disable",
        "Disable a human account.",
        "Disable a human account.",
    ),
    "accounts.master.enable": (
        "accounts.account.enable",
        "Enable a human account.",
        "Enable a human account.",
    ),
    "accounts.master.assignRole": (
        "accounts.account.replaceScopes",
        "Assign a human authorization role.",
        "Replace an account principal's exact scopes.",
    ),
    "auth.master.manageClients": (
        "auth.client.manage",
        "Manage OAuth2 clients.",
        "Manage authorization clients.",
    ),
    "auth.master.manageRoles": (
        "auth.principal.replaceScopes",
        "Manage authorization roles and role grants.",
        "Replace an authorization principal's exact scopes.",
    ),
    "auth.master.manageScopes": (
        "auth.scope.manage",
        "Manage the OAuth2 scope catalog.",
        "Manage the authorization scope catalog.",
    ),
    "auth.internal.assignPrincipalRole": (
        "auth.internal.replacePrincipalScopes",
        "Assign a human authorization role from an internal service.",
        "Replace a principal's exact scopes from an internal service.",
    ),
}

_LEGACY_ROLE_SCOPE_IDS = {
    "user": frozenset(
        {
            _SCOPE_IDS["accounts.self.getMe"],
            _SCOPE_IDS["accounts.self.updateNickname"],
        },
    ),
    "support": frozenset(
        {
            _SCOPE_IDS["accounts.self.getMe"],
            _SCOPE_IDS["accounts.self.updateNickname"],
            _SCOPE_IDS["accounts.account.read"],
        },
    ),
    "master": frozenset(
        {
            _SCOPE_IDS["accounts.self.getMe"],
            _SCOPE_IDS["accounts.self.updateNickname"],
            _SCOPE_IDS["accounts.account.read"],
            _SCOPE_IDS["accounts.staff.create"],
            _SCOPE_IDS["accounts.account.disable"],
            _SCOPE_IDS["accounts.account.enable"],
            _SCOPE_IDS["accounts.account.replaceScopes"],
            _SCOPE_IDS["auth.client.manage"],
            _SCOPE_IDS["auth.principal.replaceScopes"],
            _SCOPE_IDS["auth.scope.manage"],
        },
    ),
}

_LEGACY_ROLE_GRANTS = (
    ("user", _SCOPE_IDS["accounts.self.getMe"], True),
    ("user", _SCOPE_IDS["accounts.self.updateNickname"], True),
    ("support", _SCOPE_IDS["accounts.self.getMe"], True),
    ("support", _SCOPE_IDS["accounts.self.updateNickname"], True),
    ("support", _SCOPE_IDS["accounts.account.read"], False),
    ("master", _SCOPE_IDS["accounts.self.getMe"], True),
    ("master", _SCOPE_IDS["accounts.self.updateNickname"], True),
    ("master", _SCOPE_IDS["accounts.account.read"], False),
    ("master", _SCOPE_IDS["accounts.staff.create"], False),
    ("master", _SCOPE_IDS["accounts.account.disable"], False),
    ("master", _SCOPE_IDS["accounts.account.enable"], False),
    ("master", _SCOPE_IDS["accounts.account.replaceScopes"], False),
    ("master", _SCOPE_IDS["auth.client.manage"], False),
    ("master", _SCOPE_IDS["auth.principal.replaceScopes"], False),
    ("master", _SCOPE_IDS["auth.scope.manage"], False),
)

_AUDIENCE_PREFIX = "urn:pokerlost:service:"


def _count(connection: Connection, statement: str) -> int:
    value = connection.execute(sa.text(statement)).scalar_one()
    if type(value) is not int:
        raise RuntimeError("Migration count query returned a non-integer value")
    return value


def _require_zero(connection: Connection, statement: str, message: str) -> None:
    if _count(connection, statement) != 0:
        raise RuntimeError(message)


def _rename_constraint(table: str, previous: str, current: str) -> None:
    op.execute(sa.text(f'ALTER TABLE "{table}" RENAME CONSTRAINT "{previous}" TO "{current}"'))


def _rename_index(previous: str, current: str) -> None:
    op.execute(sa.text(f'ALTER INDEX "{previous}" RENAME TO "{current}"'))


def _migrate_scope_definitions(*, reverse: bool) -> None:
    scope_table = sa.table(
        "scope_definitions",
        sa.column("id", postgresql.UUID(as_uuid=True)),
        sa.column("name", sa.Text()),
        sa.column("description", sa.Text()),
        sa.column("updated_at", sa.DateTime(timezone=True)),
    )
    connection = op.get_bind()
    for previous, (current, previous_description, current_description) in _SCOPE_CHANGES.items():
        source_name = current if reverse else previous
        target_name = previous if reverse else current
        target_description = previous_description if reverse else current_description
        scope_id = _SCOPE_IDS[current]
        source_count = connection.execute(
            sa.select(sa.func.count())
            .select_from(scope_table)
            .where(scope_table.c.id == scope_id, scope_table.c.name == source_name),
        ).scalar_one()
        if source_count != 1:
            raise RuntimeError(
                f"Expected scope definition {source_name!r} was not found exactly once"
            )
        collision_count = connection.execute(
            sa.select(sa.func.count())
            .select_from(scope_table)
            .where(scope_table.c.name == target_name, scope_table.c.id != scope_id),
        ).scalar_one()
        if collision_count != 0:
            raise RuntimeError(f"Scope rename target {target_name!r} already exists")
        result = connection.execute(
            scope_table.update()
            .where(scope_table.c.id == scope_id, scope_table.c.name == source_name)
            .values(
                name=target_name,
                description=target_description,
                updated_at=sa.func.now(),
            ),
        )
        if result.rowcount != 1:
            raise RuntimeError(f"Scope definition {source_name!r} was not migrated")


def _validate_current_scope_catalog(connection: Connection) -> None:
    if _count(connection, "SELECT count(*) FROM scope_definitions") != len(_SCOPE_IDS):
        raise RuntimeError("Scope definition count differs from the canonical service catalogs")
    scope_table = sa.table(
        "scope_definitions",
        sa.column("id", postgresql.UUID(as_uuid=True)),
        sa.column("name", sa.Text()),
    )
    for name, scope_id in _SCOPE_IDS.items():
        count = connection.execute(
            sa.select(sa.func.count())
            .select_from(scope_table)
            .where(scope_table.c.id == scope_id, scope_table.c.name == name),
        ).scalar_one()
        if count != 1:
            raise RuntimeError(f"Canonical scope definition {name!r} is missing or inconsistent")


def _convert_audiences_to_service_names(table: str) -> None:
    connection = op.get_bind()
    source_count = _count(connection, f'SELECT count(*) FROM "{table}"')
    result = connection.execute(
        sa.text(
            f'UPDATE "{table}" SET audience = substring(audience FROM char_length(:prefix) + 1)'
        ),
        {"prefix": _AUDIENCE_PREFIX},
    )
    if result.rowcount != source_count:
        raise RuntimeError(f"Every {table} audience row must be migrated")
    _require_zero(
        connection,
        f"SELECT count(*) FROM \"{table}\" WHERE audience !~ '^[a-z][A-Za-z0-9]*$'",
        f"{table} contains an invalid service-name audience",
    )


def _convert_audiences_to_legacy_urns(table: str) -> None:
    connection = op.get_bind()
    source_count = _count(connection, f'SELECT count(*) FROM "{table}"')
    result = connection.execute(
        sa.text(f'UPDATE "{table}" SET audience = :prefix || audience'),
        {"prefix": _AUDIENCE_PREFIX},
    )
    if result.rowcount != source_count:
        raise RuntimeError(f"Every {table} audience row must be restored")


def _validate_legacy_service_grants(connection: Connection) -> None:
    for table in ("service_scope_grants", "service_audience_grants"):
        _require_zero(
            connection,
            f"SELECT count(*) FROM {table} AS grant_row "
            "JOIN authorization_principals AS principal "
            "ON principal.id = grant_row.principal_id "
            "WHERE principal.principal_type <> 'service'",
            f"{table} contains a grant for a non-service principal",
        )
    _require_zero(
        connection,
        """
        SELECT count(*)
        FROM oauth_clients AS client
        JOIN authorization_principals AS principal
          ON principal.id = client.bound_principal_id
        WHERE client.client_type = 'confidential'
          AND principal.principal_type <> 'service'
        """,
        "A confidential OAuth2 client is bound to a non-service principal",
    )


def _copy_principal_scope_grants(connection: Connection) -> None:
    expected_count = _count(
        connection,
        """
        SELECT count(*)
        FROM (
            SELECT principal.id AS principal_id, role_grant.scope_id
            FROM authorization_principals AS principal
            JOIN role_scope_grants AS role_grant ON role_grant.role_id = principal.role_id
            UNION
            SELECT principal_id, scope_id FROM service_scope_grants
        ) AS expected_grant
        """,
    )
    connection.execute(
        sa.text(
            """
            INSERT INTO principal_scope_grants (principal_id, scope_id, created_at)
            SELECT principal_id, scope_id, min(created_at)
            FROM (
                SELECT
                    principal.id AS principal_id,
                    role_grant.scope_id,
                    greatest(principal.created_at, role_grant.created_at) AS created_at
                FROM authorization_principals AS principal
                JOIN role_scope_grants AS role_grant ON role_grant.role_id = principal.role_id
                UNION ALL
                SELECT principal_id, scope_id, created_at FROM service_scope_grants
            ) AS source_grant
            GROUP BY principal_id, scope_id
            """
        ),
    )
    copied_count = _count(connection, "SELECT count(*) FROM principal_scope_grants")
    if copied_count != expected_count:
        raise RuntimeError(
            "Principal scope grant row count does not match the distinct source union"
        )
    _require_zero(
        connection,
        """
        SELECT count(*)
        FROM (
            SELECT principal.id AS principal_id, role_grant.scope_id
            FROM authorization_principals AS principal
            JOIN role_scope_grants AS role_grant ON role_grant.role_id = principal.role_id
            UNION
            SELECT principal_id, scope_id FROM service_scope_grants
        ) AS source_grant
        LEFT JOIN principal_scope_grants AS copied_grant
          ON copied_grant.principal_id = source_grant.principal_id
         AND copied_grant.scope_id = source_grant.scope_id
        WHERE copied_grant.principal_id IS NULL
        """,
        "A legacy effective grant was not copied to principal_scope_grants",
    )


def upgrade() -> None:
    """Materialize effective permissions and remove the role authorization model."""
    connection = op.get_bind()
    _validate_legacy_service_grants(connection)

    op.rename_table("oauth_scopes", "scope_definitions")
    _rename_constraint("scope_definitions", "pk_oauth_scopes", "pk_scope_definitions")
    _rename_constraint("scope_definitions", "uq_oauth_scopes_name", "uq_scope_definitions_name")
    _rename_constraint(
        "scope_definitions",
        "ck_oauth_scopes_name_format",
        "ck_scope_definitions_name_format",
    )
    _rename_constraint(
        "scope_definitions",
        "ck_oauth_scopes_description_not_empty",
        "ck_scope_definitions_description_not_empty",
    )

    op.create_table(
        "principal_scope_grants",
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
            name="fk_principal_scope_grants_principal_id_authorization_principals",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["scope_id"],
            ["scope_definitions.id"],
            name="fk_principal_scope_grants_scope_id_scope_definitions",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint(
            "principal_id",
            "scope_id",
            name="pk_principal_scope_grants",
        ),
    )
    _copy_principal_scope_grants(connection)

    op.drop_constraint(
        "fk_authorization_principals_role_id_authorization_roles",
        "authorization_principals",
        type_="foreignkey",
    )
    op.drop_column("authorization_principals", "role_id")
    op.drop_table("service_scope_grants")
    op.drop_table("role_scope_grants")
    op.drop_table("authorization_roles")

    op.create_unique_constraint(
        "uq_authorization_principals_id_principal_type",
        "authorization_principals",
        ["id", "principal_type"],
    )
    op.add_column(
        "oauth_clients",
        sa.Column("bound_principal_type", sa.String(length=16), nullable=True),
    )
    connection.execute(
        sa.text(
            """
            UPDATE oauth_clients AS client
            SET bound_principal_type = principal.principal_type
            FROM authorization_principals AS principal
            WHERE principal.id = client.bound_principal_id
            """
        ),
    )
    _require_zero(
        connection,
        """
        SELECT count(*) FROM oauth_clients
        WHERE (client_type = 'public' AND (
                 bound_principal_id IS NOT NULL OR bound_principal_type IS NOT NULL
              ))
           OR (client_type = 'confidential' AND (
                 bound_principal_id IS NULL OR bound_principal_type IS NULL
                 OR bound_principal_type <> 'service'
              ))
        """,
        "OAuth2 client principal bindings are inconsistent with service-only credentials",
    )
    op.drop_constraint("ck_oauth_clients_binding", "oauth_clients", type_="check")
    op.drop_constraint(
        "fk_oauth_clients_bound_principal_id_authorization_principals",
        "oauth_clients",
        type_="foreignkey",
    )
    op.create_check_constraint(
        "ck_oauth_clients_binding",
        "oauth_clients",
        "(client_type = 'public' AND bound_principal_id IS NULL "
        "AND bound_principal_type IS NULL) OR "
        "(client_type = 'confidential' AND bound_principal_id IS NOT NULL "
        "AND bound_principal_type IS NOT NULL "
        "AND bound_principal_type = 'service')",
    )
    op.create_foreign_key(
        "fk_oauth_clients_bound_principal_authorization_principals",
        "oauth_clients",
        "authorization_principals",
        ["bound_principal_id", "bound_principal_type"],
        ["id", "principal_type"],
        ondelete="RESTRICT",
    )

    op.rename_table("oauth_client_scope_grants", "client_scope_grants")
    _rename_constraint(
        "client_scope_grants",
        "pk_oauth_client_scope_grants",
        "pk_client_scope_grants",
    )
    _rename_constraint(
        "client_scope_grants",
        "fk_oauth_client_scope_grants_client_id_oauth_clients",
        "fk_client_scope_grants_client_id_oauth_clients",
    )
    _rename_constraint(
        "client_scope_grants",
        "fk_oauth_client_scope_grants_scope_id_oauth_scopes",
        "fk_client_scope_grants_scope_id_scope_definitions",
    )

    op.drop_constraint(
        "ck_service_audience_grants_audience_format",
        "service_audience_grants",
        type_="check",
    )
    _convert_audiences_to_service_names("service_audience_grants")
    op.rename_table("service_audience_grants", "principal_audience_grants")
    _rename_constraint(
        "principal_audience_grants",
        "pk_service_audience_grants",
        "pk_principal_audience_grants",
    )
    _rename_constraint(
        "principal_audience_grants",
        "fk_service_audience_grants_principal_authorization_principals",
        "fk_principal_audience_grants_principal_id_authorization_principals",
    )
    op.create_check_constraint(
        "ck_principal_audience_grants_audience_format",
        "principal_audience_grants",
        "audience ~ '^[a-z][A-Za-z0-9]*$'",
    )

    op.drop_constraint(
        "ck_oauth_client_audience_grants_audience_format",
        "oauth_client_audience_grants",
        type_="check",
    )
    _convert_audiences_to_service_names("oauth_client_audience_grants")
    op.rename_table("oauth_client_audience_grants", "client_audience_grants")
    _rename_constraint(
        "client_audience_grants",
        "pk_oauth_client_audience_grants",
        "pk_client_audience_grants",
    )
    _rename_constraint(
        "client_audience_grants",
        "fk_oauth_client_audience_grants_client_id_oauth_clients",
        "fk_client_audience_grants_client_id_oauth_clients",
    )
    op.create_check_constraint(
        "ck_client_audience_grants_audience_format",
        "client_audience_grants",
        "audience ~ '^[a-z][A-Za-z0-9]*$'",
    )

    op.rename_table("oauth_client_secrets", "client_credentials")
    for previous, current in (
        ("pk_oauth_client_secrets", "pk_client_credentials"),
        ("uq_oauth_client_secrets_secret_digest", "uq_client_credentials_secret_digest"),
        (
            "ck_oauth_client_secrets_secret_digest_length",
            "ck_client_credentials_secret_digest_length",
        ),
        ("ck_oauth_client_secrets_status", "ck_client_credentials_status"),
        ("ck_oauth_client_secrets_updated_at", "ck_client_credentials_updated_at"),
        ("ck_oauth_client_secrets_expires_at", "ck_client_credentials_expires_at"),
        ("ck_oauth_client_secrets_revoked_at", "ck_client_credentials_revoked_at"),
        ("ck_oauth_client_secrets_state", "ck_client_credentials_state"),
        (
            "fk_oauth_client_secrets_client_id_oauth_clients",
            "fk_client_credentials_client_id_oauth_clients",
        ),
    ):
        _rename_constraint("client_credentials", previous, current)
    _rename_index("ix_oauth_client_secrets_client_id", "ix_client_credentials_client_id")

    _migrate_scope_definitions(reverse=False)
    _validate_current_scope_catalog(connection)


def _legacy_principal_role_assignments(connection: Connection) -> dict[UUID, UUID]:
    rows = connection.execute(
        sa.text(
            """
            SELECT principal.id, principal.principal_type, grant_row.scope_id
            FROM authorization_principals AS principal
            LEFT JOIN principal_scope_grants AS grant_row
              ON grant_row.principal_id = principal.id
            ORDER BY principal.id, grant_row.scope_id
            """
        ),
    )
    principal_types: dict[UUID, str] = {}
    principal_scopes: defaultdict[UUID, set[UUID]] = defaultdict(set)
    for principal_id, principal_type, scope_id in rows:
        principal_types[principal_id] = principal_type
        if scope_id is not None:
            principal_scopes[principal_id].add(scope_id)

    role_by_scope_set = {
        scope_ids: _ROLE_IDS[role] for role, scope_ids in _LEGACY_ROLE_SCOPE_IDS.items()
    }
    assignments: dict[UUID, UUID] = {}
    for principal_id, principal_type in principal_types.items():
        if principal_type == "service":
            assignments[principal_id] = _ROLE_IDS["auto"]
            continue
        if principal_type != "human":
            raise RuntimeError("Authorization principal has an unknown principal type")
        role_id = role_by_scope_set.get(frozenset(principal_scopes[principal_id]))
        if role_id is None:
            raise RuntimeError(
                "Cannot downgrade a human principal whose scopes do not match one legacy role"
            )
        assignments[principal_id] = role_id
    return assignments


def _create_legacy_roles_and_grants() -> None:
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
            ["scope_definitions.id"],
            name="fk_role_scope_grants_scope_id_oauth_scopes",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("role_id", "scope_id", name="pk_role_scope_grants"),
    )

    role_table = sa.table(
        "authorization_roles",
        sa.column("id", postgresql.UUID(as_uuid=True)),
        sa.column("code", sa.String(length=16)),
        sa.column("principal_type", sa.String(length=16)),
    )
    grant_table = sa.table(
        "role_scope_grants",
        sa.column("role_id", postgresql.UUID(as_uuid=True)),
        sa.column("scope_id", postgresql.UUID(as_uuid=True)),
        sa.column("is_default", sa.Boolean()),
    )
    op.bulk_insert(
        role_table,
        [
            {"id": _ROLE_IDS["user"], "code": "user", "principal_type": "human"},
            {"id": _ROLE_IDS["support"], "code": "support", "principal_type": "human"},
            {"id": _ROLE_IDS["master"], "code": "master", "principal_type": "human"},
            {"id": _ROLE_IDS["auto"], "code": "auto", "principal_type": "service"},
        ],
    )
    op.bulk_insert(
        grant_table,
        [
            {"role_id": _ROLE_IDS[role], "scope_id": scope_id, "is_default": is_default}
            for role, scope_id, is_default in _LEGACY_ROLE_GRANTS
        ],
    )


def downgrade() -> None:
    """Restore the legacy schema only while every direct scope set maps without loss."""
    connection = op.get_bind()
    assignments = _legacy_principal_role_assignments(connection)
    _require_zero(
        connection,
        """
        SELECT count(*)
        FROM principal_audience_grants AS grant_row
        JOIN authorization_principals AS principal ON principal.id = grant_row.principal_id
        WHERE principal.principal_type <> 'service'
        """,
        "Cannot downgrade principal audience grants for non-service principals",
    )

    op.drop_constraint(
        "fk_oauth_clients_bound_principal_authorization_principals",
        "oauth_clients",
        type_="foreignkey",
    )
    op.drop_constraint("ck_oauth_clients_binding", "oauth_clients", type_="check")
    op.drop_column("oauth_clients", "bound_principal_type")
    op.create_check_constraint(
        "ck_oauth_clients_binding",
        "oauth_clients",
        "(client_type = 'public' AND bound_principal_id IS NULL) OR "
        "(client_type = 'confidential' AND bound_principal_id IS NOT NULL)",
    )
    op.create_foreign_key(
        "fk_oauth_clients_bound_principal_id_authorization_principals",
        "oauth_clients",
        "authorization_principals",
        ["bound_principal_id"],
        ["id"],
        ondelete="RESTRICT",
    )
    op.drop_constraint(
        "uq_authorization_principals_id_principal_type",
        "authorization_principals",
        type_="unique",
    )

    _migrate_scope_definitions(reverse=True)
    _create_legacy_roles_and_grants()
    op.add_column(
        "authorization_principals",
        sa.Column("role_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    principal_table = sa.table(
        "authorization_principals",
        sa.column("id", postgresql.UUID(as_uuid=True)),
        sa.column("role_id", postgresql.UUID(as_uuid=True)),
    )
    for principal_id, role_id in assignments.items():
        result = connection.execute(
            principal_table.update()
            .where(principal_table.c.id == principal_id)
            .values(role_id=role_id),
        )
        if result.rowcount != 1:
            raise RuntimeError("Legacy principal role assignment was not restored")
    op.alter_column("authorization_principals", "role_id", nullable=False)
    op.create_foreign_key(
        "fk_authorization_principals_role_id_authorization_roles",
        "authorization_principals",
        "authorization_roles",
        ["role_id", "principal_type"],
        ["id", "principal_type"],
        ondelete="RESTRICT",
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
            ["scope_definitions.id"],
            name="fk_service_scope_grants_scope_id_oauth_scopes",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint(
            "principal_id",
            "scope_id",
            name="pk_service_scope_grants",
        ),
    )
    connection.execute(
        sa.text(
            """
            INSERT INTO service_scope_grants (principal_id, scope_id, created_at)
            SELECT grant_row.principal_id, grant_row.scope_id, grant_row.created_at
            FROM principal_scope_grants AS grant_row
            JOIN authorization_principals AS principal ON principal.id = grant_row.principal_id
            WHERE principal.principal_type = 'service'
            """
        ),
    )
    expected_service_grants = _count(
        connection,
        """
        SELECT count(*)
        FROM principal_scope_grants AS grant_row
        JOIN authorization_principals AS principal ON principal.id = grant_row.principal_id
        WHERE principal.principal_type = 'service'
        """,
    )
    if _count(connection, "SELECT count(*) FROM service_scope_grants") != expected_service_grants:
        raise RuntimeError("Service scope grant row count was not restored")
    op.drop_table("principal_scope_grants")

    op.drop_constraint(
        "ck_principal_audience_grants_audience_format",
        "principal_audience_grants",
        type_="check",
    )
    _convert_audiences_to_legacy_urns("principal_audience_grants")
    op.rename_table("principal_audience_grants", "service_audience_grants")
    _rename_constraint(
        "service_audience_grants",
        "pk_principal_audience_grants",
        "pk_service_audience_grants",
    )
    _rename_constraint(
        "service_audience_grants",
        "fk_principal_audience_grants_principal_id_authorization_principals",
        "fk_service_audience_grants_principal_authorization_principals",
    )
    op.create_check_constraint(
        "ck_service_audience_grants_audience_format",
        "service_audience_grants",
        "audience ~ '^urn:pokerlost:service:[a-z][A-Za-z0-9]*$'",
    )

    op.drop_constraint(
        "ck_client_audience_grants_audience_format",
        "client_audience_grants",
        type_="check",
    )
    _convert_audiences_to_legacy_urns("client_audience_grants")
    op.rename_table("client_audience_grants", "oauth_client_audience_grants")
    _rename_constraint(
        "oauth_client_audience_grants",
        "pk_client_audience_grants",
        "pk_oauth_client_audience_grants",
    )
    _rename_constraint(
        "oauth_client_audience_grants",
        "fk_client_audience_grants_client_id_oauth_clients",
        "fk_oauth_client_audience_grants_client_id_oauth_clients",
    )
    op.create_check_constraint(
        "ck_oauth_client_audience_grants_audience_format",
        "oauth_client_audience_grants",
        "audience ~ '^urn:pokerlost:service:[a-z][A-Za-z0-9]*$'",
    )

    op.rename_table("client_scope_grants", "oauth_client_scope_grants")
    _rename_constraint(
        "oauth_client_scope_grants",
        "pk_client_scope_grants",
        "pk_oauth_client_scope_grants",
    )
    _rename_constraint(
        "oauth_client_scope_grants",
        "fk_client_scope_grants_client_id_oauth_clients",
        "fk_oauth_client_scope_grants_client_id_oauth_clients",
    )
    _rename_constraint(
        "oauth_client_scope_grants",
        "fk_client_scope_grants_scope_id_scope_definitions",
        "fk_oauth_client_scope_grants_scope_id_oauth_scopes",
    )

    _rename_index("ix_client_credentials_client_id", "ix_oauth_client_secrets_client_id")
    op.rename_table("client_credentials", "oauth_client_secrets")
    for previous, current in (
        ("pk_client_credentials", "pk_oauth_client_secrets"),
        ("uq_client_credentials_secret_digest", "uq_oauth_client_secrets_secret_digest"),
        (
            "ck_client_credentials_secret_digest_length",
            "ck_oauth_client_secrets_secret_digest_length",
        ),
        ("ck_client_credentials_status", "ck_oauth_client_secrets_status"),
        ("ck_client_credentials_updated_at", "ck_oauth_client_secrets_updated_at"),
        ("ck_client_credentials_expires_at", "ck_oauth_client_secrets_expires_at"),
        ("ck_client_credentials_revoked_at", "ck_oauth_client_secrets_revoked_at"),
        ("ck_client_credentials_state", "ck_oauth_client_secrets_state"),
        (
            "fk_client_credentials_client_id_oauth_clients",
            "fk_oauth_client_secrets_client_id_oauth_clients",
        ),
    ):
        _rename_constraint("oauth_client_secrets", previous, current)

    op.rename_table("scope_definitions", "oauth_scopes")
    _rename_constraint("oauth_scopes", "pk_scope_definitions", "pk_oauth_scopes")
    _rename_constraint("oauth_scopes", "uq_scope_definitions_name", "uq_oauth_scopes_name")
    _rename_constraint(
        "oauth_scopes",
        "ck_scope_definitions_name_format",
        "ck_oauth_scopes_name_format",
    )
    _rename_constraint(
        "oauth_scopes",
        "ck_scope_definitions_description_not_empty",
        "ck_oauth_scopes_description_not_empty",
    )
