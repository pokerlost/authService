"""Owned human session-list response schema."""

from __future__ import annotations

from pydantic import Field

from api.schemas.base import ResponseModel

from .session_response import SessionResponse


class SessionsListResponse(ResponseModel):
    """Deterministically ordered sessions owned by the authenticated principal."""

    sessions: list[SessionResponse] = Field(description="Newest-first owned session summaries.")
