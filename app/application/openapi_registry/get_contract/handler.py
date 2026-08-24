"""OpenAPI contract detail query orchestration."""

from __future__ import annotations

from application.errors import IntegrityError, OpenAPIContractNotFoundError
from application.openapi_registry.values import OpenAPIContractDetail
from persistence.repositories import (
    SQLAlchemyOpenAPIContractRepository,
    SQLAlchemyRegisteredServiceRepository,
)

from .query import GetOpenAPIContractQuery


class GetOpenAPIContractHandler:
    """Return one immutable document only through an explicit master read."""

    __slots__ = ("_contract_repository", "_service_repository")

    def __init__(
        self,
        *,
        service_repository: SQLAlchemyRegisteredServiceRepository,
        contract_repository: SQLAlchemyOpenAPIContractRepository,
    ) -> None:
        self._service_repository = service_repository
        self._contract_repository = contract_repository

    async def execute(self, query: GetOpenAPIContractQuery) -> OpenAPIContractDetail:
        """Resolve contract and service identity without mutating lifecycle state."""
        contract = await self._contract_repository.get_by_id(query.contract_id)
        if contract is None:
            raise OpenAPIContractNotFoundError
        service = await self._service_repository.get_by_id(contract.registered_service_id)
        if service is None:
            raise IntegrityError
        return OpenAPIContractDetail(
            contract_id=contract.id,
            service_id=service.service_id,
            contract_version=contract.contract_version,
            openapi_version=contract.openapi_version,
            schema_hash=contract.schema_hash,
            status=contract.status,
            validated_at=contract.validated_at,
            activated_at=contract.activated_at,
            retired_at=contract.retired_at,
            created_at=contract.created_at,
            updated_at=contract.updated_at,
            document=contract.document,
        )
