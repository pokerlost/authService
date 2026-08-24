"""Explicit OAuth2 scope grant control-plane requests."""

from __future__ import annotations

from pydantic import Field

from api.schemas.base import APIModel
from domain.enums import Role
from domain.types import APIOperationId, ServiceSlug


class RoleScopeRequest(APIModel):
    """One exact human role and canonical operation scope."""

    role: Role
    scope: APIOperationId


class ServiceScopeRequest(APIModel):
    """One source service, target audience, and canonical operation scope."""

    service_slug: ServiceSlug = Field(description="Canonical source SERVICE_SLUG.")
    audience: ServiceSlug = Field(description="Canonical target SERVICE_SLUG audience.")
    scope: APIOperationId


class ListServiceScopesRequest(APIModel):
    """Source service and target audience whose exact grants are listed."""

    service_slug: ServiceSlug = Field(description="Canonical source SERVICE_SLUG.")
    audience: ServiceSlug = Field(description="Canonical target SERVICE_SLUG audience.")
