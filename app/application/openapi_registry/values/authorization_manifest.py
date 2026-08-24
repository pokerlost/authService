"""Active normalized authorization manifest."""

from __future__ import annotations

from uuid import UUID

from domain.openapi_registry import NormalizedAPIOperation
from domain.types import ContractVersion, ServiceId
from domain.value_model import ValueModel


class AuthorizationManifest(ValueModel):
    """Control-plane read model for one explicitly active service contract."""

    service_id: ServiceId
    contract_id: UUID
    contract_version: ContractVersion
    schema_hash: str
    operations: list[NormalizedAPIOperation]
