"""OpenAPI contract list query orchestration."""

from __future__ import annotations

from application.errors import RegisteredServiceNotFoundError
from application.openapi_registry.values import OpenAPIContractsPage, OpenAPIContractSummary
from persistence.queries import SQLAlchemyOpenAPIRegistryQuery
from persistence.repositories import SQLAlchemyRegisteredServiceRepository

from .query import ListOpenAPIContractsQuery


class ListOpenAPIContractsHandler:
    """Return bounded contract summaries without submitted JSON documents."""

    __slots__ = ("_registry_query", "_service_repository")

    def __init__(
        self,
        *,
        service_repository: SQLAlchemyRegisteredServiceRepository,
        registry_query: SQLAlchemyOpenAPIRegistryQuery,
    ) -> None:
        self._service_repository = service_repository
        self._registry_query = registry_query

    async def execute(self, query: ListOpenAPIContractsQuery) -> OpenAPIContractsPage:
        """Read one extra row to expose a stable next contract UUID cursor."""
        service = await self._service_repository.get_by_service_id(query.service_id)
        if service is None:
            raise RegisteredServiceNotFoundError
        rows = await self._registry_query.list_contracts(
            registered_service_id=service.id,
            limit=query.limit + 1,
            after_contract_id=query.after_contract_id,
        )
        has_more = len(rows) > query.limit
        page_rows = rows[: query.limit]
        items = [
            OpenAPIContractSummary(
                contract_id=row.id,
                service_id=row.service_id,
                contract_version=row.contract_version,
                openapi_version=row.openapi_version,
                schema_hash=row.schema_hash,
                status=row.status,
                validated_at=row.validated_at,
                activated_at=row.activated_at,
                retired_at=row.retired_at,
                created_at=row.created_at,
                updated_at=row.updated_at,
            )
            for row in page_rows
        ]
        return OpenAPIContractsPage(
            items=items,
            next_cursor=items[-1].contract_id if has_more and items else None,
        )
