"""Typed projection extraction from SQLAlchemy mapping results."""

from __future__ import annotations

from sqlalchemy.engine import MappingResult, Result

from domain.value_model import ValueModel


class SQLAlchemyProjectionResultReader[ProjectionT: ValueModel]:
    """Validate labeled SQLAlchemy mappings into immutable read projections."""

    def __init__[*RowT](
        self,
        result: Result[tuple[*RowT]],
        projection_type: type[ProjectionT],
    ) -> None:
        """Keep one mapping result and its target projection type."""
        self._result: MappingResult = result.mappings()
        self._projection_type = projection_type

    def one(self) -> ProjectionT:
        """Return exactly one validated projection."""
        return self._projection_type.model_validate(self._result.one())

    def one_or_none(self) -> ProjectionT | None:
        """Return zero or one validated projection."""
        row = self._result.one_or_none()
        if row is None:
            return None
        return self._projection_type.model_validate(row)

    def all(self) -> list[ProjectionT]:
        """Materialize every validated projection in result order."""
        return [self._projection_type.model_validate(row) for row in self._result.all()]
