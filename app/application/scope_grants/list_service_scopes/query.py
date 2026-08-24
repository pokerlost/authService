"""Service scope list query."""

from __future__ import annotations

from pydantic import Field

from domain.types import ServiceSlug
from domain.value_model import ValueModel


class ListServiceScopesQuery(ValueModel):
    """Bounded exact source-service and target-resource grant list."""

    service_slug: ServiceSlug
    audience: ServiceSlug
    limit: int = Field(ge=1, le=10_000)
