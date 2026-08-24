"""Human session-management RPC router composition."""

from __future__ import annotations

from fastapi import APIRouter

from api.openapi import OpenAPITag

from .list import router as list_router
from .revoke import router as revoke_router

router = APIRouter(prefix="/sessions", tags=[OpenAPITag.SESSIONS])
router.include_router(list_router)
router.include_router(revoke_router)
