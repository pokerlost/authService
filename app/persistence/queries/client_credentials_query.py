"""SQLAlchemy client-credentials authorization query adapter."""

from __future__ import annotations

from typing import Any, cast
from uuid import UUID

from pypokerlost.enums import PokerlostScopes, PrincipalStatus, PrincipalType
from pypokerlost.types import PokerlostAudience
from sqlalchemy import cast as sql_cast
from sqlalchemy import func, literal, select
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
from persistence.database.models import (
    AuthorizationPrincipalModel,
    ClientAudienceGrantModel,
    ClientCredentialModel,
    ClientScopeGrantModel,
    OAuthClientGrantTypeModel,
    OAuthClientModel,
    PrincipalAudienceGrantModel,
    PrincipalScopeGrantModel,
    ScopeDefinitionModel,
)
from persistence.repositories import SQLAlchemyRepository


class SQLAlchemyClientCredentialsQuery(SQLAlchemyRepository, ClientCredentialsQuery):
    """Read only exact direct client and principal authorization facts."""

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
                                ClientCredentialModel.id,
                                "client_id",
                                ClientCredentialModel.client_id,
                                "secret_digest",
                                func.encode(ClientCredentialModel.secret_digest, "hex"),
                                "status",
                                ClientCredentialModel.status,
                                "created_at",
                                ClientCredentialModel.created_at,
                                "updated_at",
                                ClientCredentialModel.updated_at,
                                "expires_at",
                                ClientCredentialModel.expires_at,
                                "revoked_at",
                                ClientCredentialModel.revoked_at,
                            ),
                            ClientCredentialModel.created_at,
                            ClientCredentialModel.id,
                        ),
                    ),
                    sql_cast(literal("[]"), JSONB),
                ),
            )
            .where(ClientCredentialModel.client_id == OAuthClientModel.id)
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
        principal_scopes = (
            select(
                func.coalesce(
                    func.jsonb_agg(
                        aggregate_order_by(ScopeDefinitionModel.name, ScopeDefinitionModel.name),
                    ),
                    sql_cast(literal("[]"), JSONB),
                ),
            )
            .select_from(PrincipalScopeGrantModel)
            .join(
                ScopeDefinitionModel,
                PrincipalScopeGrantModel.scope_id == ScopeDefinitionModel.id,
            )
            .where(PrincipalScopeGrantModel.principal_id == OAuthClientModel.bound_principal_id)
            .correlate(OAuthClientModel)
            .scalar_subquery()
        )
        client_scopes = (
            select(
                func.coalesce(
                    func.jsonb_agg(
                        aggregate_order_by(ScopeDefinitionModel.name, ScopeDefinitionModel.name),
                    ),
                    sql_cast(literal("[]"), JSONB),
                ),
            )
            .select_from(ClientScopeGrantModel)
            .join(
                ScopeDefinitionModel,
                ClientScopeGrantModel.scope_id == ScopeDefinitionModel.id,
            )
            .where(ClientScopeGrantModel.client_id == OAuthClientModel.id)
            .correlate(OAuthClientModel)
            .scalar_subquery()
        )
        principal_audiences = (
            select(
                func.coalesce(
                    func.jsonb_agg(
                        aggregate_order_by(
                            PrincipalAudienceGrantModel.audience,
                            PrincipalAudienceGrantModel.audience,
                        ),
                    ),
                    sql_cast(literal("[]"), JSONB),
                ),
            )
            .where(
                PrincipalAudienceGrantModel.principal_id == OAuthClientModel.bound_principal_id,
            )
            .correlate(OAuthClientModel)
            .scalar_subquery()
        )
        client_audiences = (
            select(
                func.coalesce(
                    func.jsonb_agg(
                        aggregate_order_by(
                            ClientAudienceGrantModel.audience,
                            ClientAudienceGrantModel.audience,
                        ),
                    ),
                    sql_cast(literal("[]"), JSONB),
                ),
            )
            .where(ClientAudienceGrantModel.client_id == OAuthClientModel.id)
            .correlate(OAuthClientModel)
            .scalar_subquery()
        )

        result = await self._session.execute(
            select(
                OAuthClientModel,
                AuthorizationPrincipalModel,
                credentials,
                grant_types,
                principal_scopes,
                client_scopes,
                principal_audiences,
                client_audiences,
            )
            .select_from(OAuthClientModel)
            .outerjoin(
                AuthorizationPrincipalModel,
                OAuthClientModel.bound_principal_id == AuthorizationPrincipalModel.id,
            )
            .where(OAuthClientModel.id == client_id),
        )
        row = result.one_or_none()
        if row is None:
            return None
        client = cast(OAuthClientModel, row[0])
        principal = cast(AuthorizationPrincipalModel | None, row[1])
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
            principal_status=(PrincipalStatus(principal.status) if principal is not None else None),
            credentials=tuple(
                _credential_from_json(item) for item in cast(list[dict[str, Any]], row[2])
            ),
            grant_types=frozenset(OAuthGrantType(value) for value in cast(list[str], row[3])),
            principal_scopes=_parse_scope_values(cast(list[str], row[4])),
            client_scopes=_parse_scope_values(cast(list[str], row[5])),
            principal_audiences=frozenset(
                PokerlostAudience(value) for value in cast(list[str], row[6])
            ),
            client_audiences=frozenset(
                PokerlostAudience(value) for value in cast(list[str], row[7])
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


def _parse_scope_values(values: list[str]) -> frozenset[PokerlostScopes]:
    """Validate persisted scope identifiers through the generated global enum."""
    return frozenset(PokerlostScopes(value) for value in values)
