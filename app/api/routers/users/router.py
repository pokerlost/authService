"""User RPC router composition."""

from __future__ import annotations

from fastapi import APIRouter

from api.openapi import OpenAPITag

from .register import router as register_router

router = APIRouter(prefix="/users", tags=[OpenAPITag.USERS])
router.include_router(register_router)
