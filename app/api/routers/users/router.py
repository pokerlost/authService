"""User router composition."""

from __future__ import annotations

from fastapi import APIRouter

from .register import router as register_router

router = APIRouter(prefix="/users")
router.include_router(register_router)
