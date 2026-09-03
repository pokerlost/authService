"""Authorization scope definition query port."""

from __future__ import annotations

from collections.abc import Collection
from typing import Protocol

from pypokerlost.enums import PokerlostScopes

from domain.scope_definition import ScopeDefinition


class ScopeDefinitionQuery(Protocol):
    """Read exact persisted scope definitions."""

    async def get_by_exact_names(
        self,
        names: Collection[PokerlostScopes],
    ) -> tuple[ScopeDefinition, ...]:
        """Return every requested catalog scope or fail when any is absent."""
        ...
