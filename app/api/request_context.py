"""Per-request identifiers and safe observability propagation."""

from __future__ import annotations

import re
from collections.abc import Awaitable, Callable
from uuid import uuid4

import logfire
from fastapi import FastAPI, Request, Response

from .types import RequestContext

REQUEST_ID_HEADER = "X-Request-ID"
CORRELATION_ID_HEADER = "X-Correlation-ID"
_CORRELATION_ID_PATTERN = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:/-]{0,127}\Z")


def _resolve_correlation_id(request: Request, request_id: str) -> str:
    supplied_id = request.headers.get(CORRELATION_ID_HEADER)
    if supplied_id is not None and _CORRELATION_ID_PATTERN.fullmatch(supplied_id):
        return supplied_id
    return request_id


def configure_request_context(application: FastAPI) -> None:
    """Attach server-owned request context and response headers."""

    @application.middleware("http")
    async def request_context_middleware(
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        request_id = str(uuid4())
        correlation_id = _resolve_correlation_id(request, request_id)
        request.state.request_context = RequestContext(
            request_id=request_id,
            correlation_id=correlation_id,
        )

        with logfire.set_baggage(
            request_id=request_id,
            correlation_id=correlation_id,
        ):
            response = await call_next(request)

        response.headers[REQUEST_ID_HEADER] = request_id
        response.headers[CORRELATION_ID_HEADER] = correlation_id
        return response
