"""Registered-service list query orchestration."""

from __future__ import annotations

from application.openapi_registry.values import RegisteredServicesPage, RegisteredServiceSummary
from persistence.queries import SQLAlchemyOpenAPIRegistryQuery

from .query import ListRegisteredServicesQuery


class ListRegisteredServicesHandler:
    """Return one bounded deterministic service registry page."""

    __slots__ = ("_registry_query",)

    def __init__(self, registry_query: SQLAlchemyOpenAPIRegistryQuery) -> None:
        self._registry_query = registry_query

    async def execute(self, query: ListRegisteredServicesQuery) -> RegisteredServicesPage:
        """Read one extra row to expose a stable next keyset cursor."""
        rows = await self._registry_query.list_registered_services(
            limit=query.limit + 1,
            after_service_id=query.after_service_id,
        )
        has_more = len(rows) > query.limit
        page_rows = rows[: query.limit]
        items = [
            RegisteredServiceSummary(
                id=row.id,
                service_id=row.service_id,
                created_at=row.created_at,
                updated_at=row.updated_at,
            )
            for row in page_rows
        ]
        return RegisteredServicesPage(
            items=items,
            next_cursor=items[-1].service_id if has_more and items else None,
        )
