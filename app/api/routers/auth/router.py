"""Authentication RPC router composition."""

from __future__ import annotations

from fastapi import APIRouter

from api.openapi import OpenAPITag

from .logout import router as logout_router
from .logout_all import router as logout_all_router

router = APIRouter(prefix="/auth", tags=[OpenAPITag.AUTH])
router.include_router(logout_router)
router.include_router(logout_all_router)
