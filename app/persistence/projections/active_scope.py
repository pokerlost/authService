"""Active canonical OAuth2 scope ownership projection."""

from __future__ import annotations

from domain.types import APIOperationId, ServiceId
from domain.value_model import ValueModel


class ActiveScopeProjection(ValueModel):
    """One currently active canonical operation scope and owning service ID."""

    api_operation_id: APIOperationId
    owner_service_id: ServiceId
