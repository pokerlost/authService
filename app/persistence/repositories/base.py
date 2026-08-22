"""Small shared SQLAlchemy repository execution base."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.selectable import TypedReturnsRows

from persistence.database.mixins import UUIDModel
from persistence.database.result_readers import SQLAlchemyScalarResultReader


class SQLAlchemyRepository:
    """Own one request session and typed scalar statement execution."""

    __slots__ = ("_session",)

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def _execute_scalars[ResultT](
        self,
        statement: TypedReturnsRows[tuple[ResultT]],
    ) -> SQLAlchemyScalarResultReader[ResultT]:
        result = await self._session.scalars(statement)
        return SQLAlchemyScalarResultReader(result)


class SQLAlchemyEntityRepository[EntityT: UUIDModel](SQLAlchemyRepository):
    """Provide standard UUID lookup for one mapped entity type."""

    __slots__ = ("_model",)

    def __init__(self, session: AsyncSession, model: type[EntityT]) -> None:
        super().__init__(session)
        self._model = model

    async def get_by_id(self, model_id: UUID) -> EntityT | None:
        """Return one UUID entity or no row."""
        statement = select(self._model).where(self._model.id == model_id)
        result = await self._execute_scalars(statement)
        return result.one_or_none()
