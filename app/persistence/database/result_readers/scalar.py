"""Typed SQLAlchemy scalar result extraction."""

from __future__ import annotations

from sqlalchemy.engine import ScalarResult


class SQLAlchemyScalarResultReader[ResultT]:
    """Centralize approved scalar result cardinality operations."""

    __slots__ = ("_result",)

    def __init__(self, result: ScalarResult[ResultT]) -> None:
        self._result = result

    def one(self) -> ResultT:
        """Return exactly one scalar value."""
        return self._result.one()

    def one_or_none(self) -> ResultT | None:
        """Return zero or one scalar value."""
        return self._result.one_or_none()

    def all(self) -> list[ResultT]:
        """Materialize all scalar values."""
        return list(self._result.all())
