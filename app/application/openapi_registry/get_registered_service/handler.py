"""Registered-service detail query orchestration."""

from __future__ import annotations

from application.errors import RegisteredServiceNotFoundError
from application.openapi_registry.values import RegisteredServiceSummary
from persistence.repositories import SQLAlchemyRegisteredServiceRepository

from .query import GetRegisteredServiceQuery


class GetRegisteredServiceHandler:
    """Return one control-plane service identity without implementation metadata."""

    __slots__ = ("_repository",)

    def __init__(self, repository: SQLAlchemyRegisteredServiceRepository) -> None:
        self._repository = repository

    async def execute(self, query: GetRegisteredServiceQuery) -> RegisteredServiceSummary:
        """Resolve one registered service by its exact platform ID."""
        service = await self._repository.get_by_service_id(query.service_id)
        if service is None:
            raise RegisteredServiceNotFoundError
        return RegisteredServiceSummary(
            id=service.id,
            service_id=service.service_id,
            created_at=service.created_at,
            updated_at=service.updated_at,
        )
