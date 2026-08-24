"""Authenticated account router composition."""

from __future__ import annotations

from fastapi import APIRouter

from api.openapi import OpenAPITag

from .change_password import router as change_password_router

router = APIRouter(prefix="/account", tags=[OpenAPITag.ACCOUNT])
router.include_router(change_password_router)
