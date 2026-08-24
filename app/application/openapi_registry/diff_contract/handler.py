"""OpenAPI contract diff query orchestration."""

from __future__ import annotations

from application.errors import OpenAPIContractNotFoundError, OpenAPIContractNotValidatedError
from application.openapi_registry.contract_diff_calculator import OpenAPIContractDiffCalculator
from application.openapi_registry.stored_operation_materializer import (
    materialize_stored_operations,
)
from application.openapi_registry.values import OpenAPIContractDiff
from domain.enums import OpenAPIContractStatus
from persistence.queries import SQLAlchemyOpenAPIRegistryQuery
from persistence.repositories import SQLAlchemyOpenAPIContractRepository

from .query import DiffOpenAPIContractQuery


class DiffOpenAPIContractHandler:
    """Compare one validated candidate against the currently active contract."""

    __slots__ = ("_calculator", "_contract_repository", "_registry_query")

    def __init__(
        self,
        *,
        contract_repository: SQLAlchemyOpenAPIContractRepository,
        registry_query: SQLAlchemyOpenAPIRegistryQuery,
        calculator: OpenAPIContractDiffCalculator,
    ) -> None:
        self._contract_repository = contract_repository
        self._registry_query = registry_query
        self._calculator = calculator

    async def execute(self, query: DiffOpenAPIContractQuery) -> OpenAPIContractDiff:
        """Return a deterministic candidate-specific diff and acknowledgement requirement."""
        candidate = await self._contract_repository.get_by_id(query.contract_id)
        if candidate is None:
            raise OpenAPIContractNotFoundError
        if candidate.status is OpenAPIContractStatus.REGISTERED:
            raise OpenAPIContractNotValidatedError
        active = await self._contract_repository.get_active_by_service_id(
            candidate.registered_service_id
        )
        candidate_operations = materialize_stored_operations(
            await self._registry_query.list_operation_policies(candidate.id)
        )
        base_operations = (
            materialize_stored_operations(
                await self._registry_query.list_operation_policies(active.id)
            )
            if active is not None
            else []
        )
        return self._calculator.calculate(
            base_contract_id=active.id if active is not None else None,
            candidate_contract_id=candidate.id,
            base_operations=base_operations,
            candidate_operations=candidate_operations,
        )
