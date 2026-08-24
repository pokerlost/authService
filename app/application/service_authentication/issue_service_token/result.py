"""Issued AUTO service token result."""

from __future__ import annotations

from uuid import UUID

from pydantic import Field

from domain.value_model import ValueModel


class IssueServiceTokenResult(ValueModel):
    """One short-lived machine access token without refresh state."""

    access_token: str = Field(repr=False)
    scopes: frozenset[str]
    principal_id: UUID
