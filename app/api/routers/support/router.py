"""Support-safe router composition."""

from __future__ import annotations

from fastapi import APIRouter

from api.openapi import OpenAPITag

from .get_user_account import router as get_user_account_router

router = APIRouter(prefix="/support", tags=[OpenAPITag.SUPPORT])
router.include_router(get_user_account_router)
