"""Service scope list query handler."""

from __future__ import annotations

from application.errors import ServicePrincipalNotFound
from persistence.database.models import ServiceScopeGrantModel
from persistence.repositories import (
    SQLAlchemyServicePrincipalRepository,
    SQLAlchemyServiceScopeGrantRepository,
)

from .query import ListServiceScopesQuery


class ListServiceScopesHandler:
    """Return one bounded source and resource scope grant list."""

    __slots__ = ("_grant_repository", "_service_principal_repository")

    def __init__(
        self,
        *,
        service_principal_repository: SQLAlchemyServicePrincipalRepository,
        grant_repository: SQLAlchemyServiceScopeGrantRepository,
    ) -> None:
        self._service_principal_repository = service_principal_repository
        self._grant_repository = grant_repository

    async def execute(
        self,
        query: ListServiceScopesQuery,
    ) -> list[ServiceScopeGrantModel]:
        """Resolve the source service and list exact target grants."""
        service_principal = await self._service_principal_repository.get_by_service_slug(
            query.service_slug
        )
        if service_principal is None:
            raise ServicePrincipalNotFound
        return await self._grant_repository.list_for_service_resource(
            service_principal_id=service_principal.principal_id,
            audience=query.audience,
            limit=query.limit,
        )
