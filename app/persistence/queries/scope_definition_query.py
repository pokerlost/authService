"""SQLAlchemy authorization scope definition query adapter."""

from __future__ import annotations

from collections.abc import Collection

from pypokerlost.enums import PokerlostScopes
from sqlalchemy import select

from application.errors import ScopeNotFoundError
from application.ports import ScopeDefinitionQuery
from domain.scope_definition import ScopeDefinition
from persistence.database.models import ScopeDefinitionModel
from persistence.repositories import SQLAlchemyRepository


class SQLAlchemyScopeDefinitionQuery(SQLAlchemyRepository, ScopeDefinitionQuery):
    """Read exact persisted scope definitions."""

    async def get_by_exact_names(
        self,
        names: Collection[PokerlostScopes],
    ) -> tuple[ScopeDefinition, ...]:
        """Return exact requested definitions or fail closed when one is absent."""
        requested_names = frozenset(names)
        if not requested_names:
            return ()
        result = await self._read_scalar(
            select(ScopeDefinitionModel)
            .where(ScopeDefinitionModel.name.in_(scope.value for scope in requested_names))
            .order_by(ScopeDefinitionModel.name),
        )
        models = result.all()
        if {model.name for model in models} != {scope.value for scope in requested_names}:
            raise ScopeNotFoundError
        return tuple(
            ScopeDefinition(
                scope_id=model.id,
                name=PokerlostScopes(model.name),
                description=model.description,
                created_at=model.created_at,
                updated_at=model.updated_at,
            )
            for model in models
        )
