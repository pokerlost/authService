"""Support-safe ordinary-user lookup request."""

from __future__ import annotations

from pydantic import Field

from api.schemas.base import APIModel
from application.support import GetUserAccountQuery
from domain.types import Username


class GetUserAccountRequest(APIModel):
    """Canonical ordinary-user login identifier kept out of URL and query logs."""

    username: Username = Field(description="Canonical ordinary-user login identifier.")

    def to_query(self) -> GetUserAccountQuery:
        """Map validated transport input to a support-safe query."""
        return GetUserAccountQuery(username=self.username)
