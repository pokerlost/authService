"""Active authorization manifest query orchestration."""

from __future__ import annotations

from application.errors import OpenAPIContractNotFoundError, RegisteredServiceNotFoundError
from application.openapi_registry.stored_operation_materializer import (
    materialize_stored_operations,
)
from application.openapi_registry.values import AuthorizationManifest
from persistence.queries import SQLAlchemyOpenAPIRegistryQuery
from persistence.repositories import (
    SQLAlchemyOpenAPIContractRepository,
    SQLAlchemyRegisteredServiceRepository,
)

from .query import GetAuthorizationManifestQuery


class GetAuthorizationManifestHandler:
    """Return only the explicitly active normalized contract read model."""

    __slots__ = ("_contract_repository", "_registry_query", "_service_repository")

    def __init__(
        self,
        *,
        service_repository: SQLAlchemyRegisteredServiceRepository,
        contract_repository: SQLAlchemyOpenAPIContractRepository,
        registry_query: SQLAlchemyOpenAPIRegistryQuery,
    ) -> None:
        self._service_repository = service_repository
        self._contract_repository = contract_repository
        self._registry_query = registry_query

    async def execute(self, query: GetAuthorizationManifestQuery) -> AuthorizationManifest:
        """Read normalized active state without creating a runtime authorization gateway."""
        service = await self._service_repository.get_by_service_id(query.service_id)
        if service is None:
            raise RegisteredServiceNotFoundError
        contract = await self._contract_repository.get_active_by_service_id(service.id)
        if contract is None:
            raise OpenAPIContractNotFoundError
        operations = materialize_stored_operations(
            await self._registry_query.list_operation_policies(contract.id)
        )
        return AuthorizationManifest(
            service_id=service.service_id,
            contract_id=contract.id,
            contract_version=contract.contract_version,
            schema_hash=contract.schema_hash,
            operations=operations,
        )
