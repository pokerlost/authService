"""SQLAlchemy client-credentials authorization query adapter."""

from __future__ import annotations

from typing import Any, cast
from uuid import UUID

from pypokerlost.contracts.authorization import (
    AuthorizationRole,
    PrincipalStatus,
    PrincipalType,
)
from pypokerlost.types import OAuthScope, parse_oauth_scope_string
from sqlalchemy import and_, func, literal, select
from sqlalchemy import cast as sql_cast
from sqlalchemy.dialects.postgresql import JSONB, aggregate_order_by

from application.ports import (
    ClientCredentialsAuthorizationContext,
    ClientCredentialsQuery,
)
from domain.enums import (
    OAuthClientStatus,
    OAuthClientType,
    OAuthGrantType,
)
from domain.oauth_client_credential import OAuthClientCredential
from domain.resource_indicator import ResourceIndicator
from persistence.database.models import (
    AuthorizationPrincipalModel,
    AuthorizationRoleModel,
    OAuthClientAudienceGrantModel,
    OAuthClientGrantTypeModel,
    OAuthClientModel,
    OAuthClientScopeGrantModel,
    OAuthClientSecretModel,
    OAuthScopeModel,
    ServiceAudienceGrantModel,
    ServiceScopeGrantModel,
)
from persistence.repositories import SQLAlchemyRepository


class SQLAlchemyClientCredentialsQuery(SQLAlchemyRepository, ClientCredentialsQuery):
    """Read only exact direct client and service authorization facts."""

    async def get_authorization_context(
        self,
        client_id: UUID,
    ) -> ClientCredentialsAuthorizationContext | None:
        """Return authorization facts from one PostgreSQL statement snapshot."""
        credentials = (
            select(
                func.coalesce(
                    func.jsonb_agg(
                        aggregate_order_by(
                            func.jsonb_build_object(
                                "credential_id",
                                OAuthClientSecretModel.id,
                                "client_id",
                                OAuthClientSecretModel.client_id,
                                "secret_digest",
                                func.encode(OAuthClientSecretModel.secret_digest, "hex"),
                                "status",
                                OAuthClientSecretModel.status,
                                "created_at",
                                OAuthClientSecretModel.created_at,
                                "updated_at",
                                OAuthClientSecretModel.updated_at,
                                "expires_at",
                                OAuthClientSecretModel.expires_at,
                                "revoked_at",
                                OAuthClientSecretModel.revoked_at,
                            ),
                            OAuthClientSecretModel.created_at,
                            OAuthClientSecretModel.id,
                        ),
                    ),
                    sql_cast(literal("[]"), JSONB),
                ),
            )
            .where(OAuthClientSecretModel.client_id == OAuthClientModel.id)
            .correlate(OAuthClientModel)
            .scalar_subquery()
        )
        grant_types = (
            select(
                func.coalesce(
                    func.jsonb_agg(
                        aggregate_order_by(
                            OAuthClientGrantTypeModel.grant_type,
                            OAuthClientGrantTypeModel.grant_type,
                        ),
                    ),
                    sql_cast(literal("[]"), JSONB),
                ),
            )
            .where(OAuthClientGrantTypeModel.client_id == OAuthClientModel.id)
            .correlate(OAuthClientModel)
            .scalar_subquery()
        )
        service_scopes = (
            select(
                func.coalesce(
                    func.jsonb_agg(
                        aggregate_order_by(OAuthScopeModel.name, OAuthScopeModel.name),
                    ),
                    sql_cast(literal("[]"), JSONB),
                ),
            )
            .select_from(ServiceScopeGrantModel)
            .join(OAuthScopeModel, ServiceScopeGrantModel.scope_id == OAuthScopeModel.id)
            .where(ServiceScopeGrantModel.principal_id == OAuthClientModel.bound_principal_id)
            .correlate(OAuthClientModel)
            .scalar_subquery()
        )
        client_scopes = (
            select(
                func.coalesce(
                    func.jsonb_agg(
                        aggregate_order_by(OAuthScopeModel.name, OAuthScopeModel.name),
                    ),
                    sql_cast(literal("[]"), JSONB),
                ),
            )
            .select_from(OAuthClientScopeGrantModel)
            .join(OAuthScopeModel, OAuthClientScopeGrantModel.scope_id == OAuthScopeModel.id)
            .where(OAuthClientScopeGrantModel.client_id == OAuthClientModel.id)
            .correlate(OAuthClientModel)
            .scalar_subquery()
        )
        service_audiences = (
            select(
                func.coalesce(
                    func.jsonb_agg(
                        aggregate_order_by(
                            ServiceAudienceGrantModel.audience,
                            ServiceAudienceGrantModel.audience,
                        ),
                    ),
                    sql_cast(literal("[]"), JSONB),
                ),
            )
            .where(
                ServiceAudienceGrantModel.principal_id == OAuthClientModel.bound_principal_id,
            )
            .correlate(OAuthClientModel)
            .scalar_subquery()
        )
        client_audiences = (
            select(
                func.coalesce(
                    func.jsonb_agg(
                        aggregate_order_by(
                            OAuthClientAudienceGrantModel.audience,
                            OAuthClientAudienceGrantModel.audience,
                        ),
                    ),
                    sql_cast(literal("[]"), JSONB),
                ),
            )
            .where(OAuthClientAudienceGrantModel.client_id == OAuthClientModel.id)
            .correlate(OAuthClientModel)
            .scalar_subquery()
        )

        result = await self._session.execute(
            select(
                OAuthClientModel,
                AuthorizationPrincipalModel,
                AuthorizationRoleModel.code,
                credentials,
                grant_types,
                service_scopes,
                client_scopes,
                service_audiences,
                client_audiences,
            )
            .select_from(OAuthClientModel)
            .outerjoin(
                AuthorizationPrincipalModel,
                OAuthClientModel.bound_principal_id == AuthorizationPrincipalModel.id,
            )
            .outerjoin(
                AuthorizationRoleModel,
                and_(
                    AuthorizationPrincipalModel.role_id == AuthorizationRoleModel.id,
                    AuthorizationPrincipalModel.principal_type
                    == AuthorizationRoleModel.principal_type,
                ),
            )
            .where(OAuthClientModel.id == client_id),
        )
        row = result.one_or_none()
        if row is None:
            return None
        client = cast(OAuthClientModel, row[0])
        principal = cast(AuthorizationPrincipalModel | None, row[1])
        role_code = cast(str | None, row[2])
        principal_id = principal.id if principal is not None else None
        return ClientCredentialsAuthorizationContext(
            client_id=client.id,
            client_type=OAuthClientType(client.client_type),
            client_status=OAuthClientStatus(client.status),
            bound_principal_id=client.bound_principal_id,
            principal_id=principal_id,
            principal_type=(
                PrincipalType(principal.principal_type) if principal is not None else None
            ),
            principal_role=AuthorizationRole(role_code) if role_code is not None else None,
            principal_status=(PrincipalStatus(principal.status) if principal is not None else None),
            service_slug=principal.service_slug if principal is not None else None,
            credentials=tuple(
                _credential_from_json(item) for item in cast(list[dict[str, Any]], row[3])
            ),
            grant_types=frozenset(OAuthGrantType(value) for value in cast(list[str], row[4])),
            service_scopes=_parse_scope_values(cast(list[str], row[5])),
            client_scopes=_parse_scope_values(cast(list[str], row[6])),
            service_audiences=frozenset(
                ResourceIndicator.parse(value) for value in cast(list[str], row[7])
            ),
            client_audiences=frozenset(
                ResourceIndicator.parse(value) for value in cast(list[str], row[8])
            ),
        )


def _credential_from_json(value: dict[str, Any]) -> OAuthClientCredential:
    """Restore one immutable digest-only credential from PostgreSQL JSON."""
    secret_digest = value.get("secret_digest")
    if not isinstance(secret_digest, str):
        raise TypeError("OAuth2 client secret digest encoding is invalid")
    return OAuthClientCredential.model_validate(
        value | {"secret_digest": bytes.fromhex(secret_digest)},
    )


def _parse_scope_values(values: list[str]) -> frozenset[OAuthScope]:
    """Validate persisted scope identifiers through the shared canonical parser."""
    if not values:
        return frozenset()
    return frozenset(parse_oauth_scope_string(" ".join(values)))
