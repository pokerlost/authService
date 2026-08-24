"""Human session establishment command."""

from __future__ import annotations

from uuid import UUID

from domain.value_model import ValueModel


class EstablishSessionCommand(ValueModel):
    """Server-owned principal identity for a new human session."""

    principal_id: UUID
    scopes: frozenset[str]
