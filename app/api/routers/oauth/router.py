"""OAuth2 router composition."""

from __future__ import annotations

from fastapi import APIRouter

from api.openapi import OpenAPITag

from .token import router as token_router

router = APIRouter(prefix="/oauth", tags=[OpenAPITag.OAUTH])
router.include_router(token_router)
