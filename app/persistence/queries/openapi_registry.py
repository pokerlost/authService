"""Optimized OpenAPI registry read queries."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select

from persistence.database.models import (
    ApiOperationModel,
    OpenApiContractModel,
    RegisteredServiceModel,
)
from persistence.projections import (
    OpenAPIContractListItemProjection,
    OperationAuthorizationProjection,
    RegisteredServiceListItemProjection,
)
from persistence.repositories.base import SQLAlchemyRepository


class SQLAlchemyOpenAPIRegistryQuery(SQLAlchemyRepository):
    """Read registry lists and normalized policy joins without returning raw rows."""

    async def list_registered_services(
        self,
        *,
        limit: int,
        after_service_id: str | None,
    ) -> list[RegisteredServiceListItemProjection]:
        """Read one bounded service-ID keyset page in deterministic order."""
        statement = select(
            RegisteredServiceModel.id.label("id"),
            RegisteredServiceModel.service_id.label("service_id"),
            RegisteredServiceModel.created_at.label("created_at"),
            RegisteredServiceModel.updated_at.label("updated_at"),
        ).order_by(RegisteredServiceModel.service_id)
        if after_service_id is not None:
            statement = statement.where(RegisteredServiceModel.service_id > after_service_id)
        result = await self._read_projection(
            statement.limit(limit),
            RegisteredServiceListItemProjection,
        )
        return result.all()

    async def list_contracts(
        self,
        *,
        registered_service_id: UUID,
        limit: int,
        after_contract_id: UUID | None,
    ) -> list[OpenAPIContractListItemProjection]:
        """Read one bounded UUID-keyset contract summary page for one service."""
        statement = (
            select(
                OpenApiContractModel.id.label("id"),
                RegisteredServiceModel.service_id.label("service_id"),
                OpenApiContractModel.contract_version.label("contract_version"),
                OpenApiContractModel.openapi_version.label("openapi_version"),
                OpenApiContractModel.schema_hash.label("schema_hash"),
                OpenApiContractModel.status.label("status"),
                OpenApiContractModel.validated_at.label("validated_at"),
                OpenApiContractModel.activated_at.label("activated_at"),
                OpenApiContractModel.retired_at.label("retired_at"),
                OpenApiContractModel.created_at.label("created_at"),
                OpenApiContractModel.updated_at.label("updated_at"),
            )
            .join(
                RegisteredServiceModel,
                RegisteredServiceModel.id == OpenApiContractModel.registered_service_id,
            )
            .where(OpenApiContractModel.registered_service_id == registered_service_id)
            .order_by(OpenApiContractModel.id)
        )
        if after_contract_id is not None:
            statement = statement.where(OpenApiContractModel.id > after_contract_id)
        result = await self._read_projection(
            statement.limit(limit),
            OpenAPIContractListItemProjection,
        )
        return result.all()

    async def list_operation_policies(
        self,
        contract_id: UUID,
    ) -> list[OperationAuthorizationProjection]:
        """Read normalized operations with public or exact OAuth2 authorization."""
        result = await self._read_projection(
            select(
                ApiOperationModel.id.label("api_operation_row_id"),
                ApiOperationModel.api_operation_id.label("api_operation_id"),
                ApiOperationModel.http_method.label("http_method"),
                ApiOperationModel.path.label("path"),
                ApiOperationModel.authorization_mode.label("mode"),
                ApiOperationModel.required_scope.label("required_scope"),
            )
            .where(ApiOperationModel.contract_id == contract_id)
            .order_by(ApiOperationModel.api_operation_id),
            OperationAuthorizationProjection,
        )
        return result.all()
