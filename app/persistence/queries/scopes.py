"""Active OAuth2 scope and explicit grant read queries."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import Select, and_, or_, select

from domain.authservice_scopes import AUTH_SERVICE_PROTECTED_SCOPE_IDS
from domain.enums import OpenAPIContractStatus, OperationAuthorizationMode, Role
from persistence.database.models import (
    ApiOperationModel,
    OpenApiContractModel,
    OperationIdentityModel,
    RegisteredServiceModel,
    RoleScopeGrantModel,
    ServiceScopeGrantModel,
)
from persistence.projections import ActiveScopeProjection
from persistence.repositories.base import SQLAlchemyRepository


class SQLAlchemyScopeQuery(SQLAlchemyRepository):
    """Resolve grants only through active operation identities and exact owners."""

    async def list_active_for_role(self, role: Role) -> list[ActiveScopeProjection]:
        """Return all currently active scopes explicitly granted to one human role."""
        statement = self._active_scope_statement().join(
            RoleScopeGrantModel,
            and_(
                RoleScopeGrantModel.api_operation_id == OperationIdentityModel.api_operation_id,
                RoleScopeGrantModel.role == role,
            ),
        )
        return await self._read_scopes(statement)

    async def list_active_for_service(
        self,
        *,
        service_principal_id: UUID,
        audience: str,
    ) -> list[ActiveScopeProjection]:
        """Return active scopes explicitly granted for one source and target resource."""
        statement = self._active_scope_statement().join(
            ServiceScopeGrantModel,
            and_(
                ServiceScopeGrantModel.api_operation_id == OperationIdentityModel.api_operation_id,
                ServiceScopeGrantModel.service_principal_id == service_principal_id,
                ServiceScopeGrantModel.audience == audience,
            ),
        )
        return await self._read_scopes(statement)

    async def get_active(self, api_operation_id: str) -> ActiveScopeProjection | None:
        """Return active ownership for one canonical operation scope."""
        result = await self._read_projection(
            self._active_scope_statement().where(
                OperationIdentityModel.api_operation_id == api_operation_id,
            ),
            ActiveScopeProjection,
        )
        return result.one_or_none()

    def _active_scope_statement(self) -> Select[tuple[str, str]]:
        built_in_authservice_scope = and_(
            RegisteredServiceModel.service_id == "authService",
            OperationIdentityModel.api_operation_id.in_(AUTH_SERVICE_PROTECTED_SCOPE_IDS),
        )
        active_contract_scope = and_(
            OpenApiContractModel.status == OpenAPIContractStatus.ACTIVE,
            ApiOperationModel.authorization_mode == OperationAuthorizationMode.OAUTH2,
            ApiOperationModel.required_scope == OperationIdentityModel.api_operation_id,
        )
        return (
            select(
                OperationIdentityModel.api_operation_id.label("api_operation_id"),
                RegisteredServiceModel.service_id.label("owner_service_id"),
            )
            .join(
                RegisteredServiceModel,
                RegisteredServiceModel.id == OperationIdentityModel.registered_service_id,
            )
            .outerjoin(
                ApiOperationModel,
                ApiOperationModel.api_operation_id == OperationIdentityModel.api_operation_id,
            )
            .outerjoin(
                OpenApiContractModel,
                OpenApiContractModel.id == ApiOperationModel.contract_id,
            )
            .where(or_(built_in_authservice_scope, active_contract_scope))
            .distinct()
            .order_by(OperationIdentityModel.api_operation_id)
        )

    async def _read_scopes(
        self,
        statement: Select[tuple[str, str]],
    ) -> list[ActiveScopeProjection]:
        result = await self._read_projection(statement, ActiveScopeProjection)
        return result.all()
