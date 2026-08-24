"""Explicit service scope grant responses."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from api.schemas.base import ResponseModel
from domain.types import APIOperationId, ServiceSlug


class ServiceScopeGrantResponse(ResponseModel):
    """One source-service, target-resource, and operation scope grant."""

    service_principal_id: UUID
    audience: ServiceSlug
    scope: APIOperationId
    created_at: datetime


class ServiceScopesResponse(ResponseModel):
    """Bounded deterministic list of one service resource's scope grants."""

    items: list[ServiceScopeGrantResponse]
