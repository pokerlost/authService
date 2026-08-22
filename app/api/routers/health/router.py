"""Health router composition."""

from __future__ import annotations

from fastapi import APIRouter

from .liveness import router as liveness_router
from .readiness import router as readiness_router

router = APIRouter()
router.include_router(liveness_router)
router.include_router(readiness_router)
