"""Top-level API router registration."""

from __future__ import annotations

from fastapi import FastAPI

from .routers.account import router as account_router
from .routers.auth import router as auth_router
from .routers.jwks import router as jwks_router
from .routers.master import router as master_router
from .routers.oauth import router as oauth_router
from .routers.openapi_document import router as openapi_document_router
from .routers.root import router as root_router
from .routers.sessions import router as sessions_router
from .routers.support import router as support_router
from .routers.users import router as users_router


def configure_routes(application: FastAPI) -> None:
    """Register all public routers on the application."""
    application.include_router(root_router)
    application.include_router(jwks_router)
    application.include_router(users_router)
    application.include_router(account_router)
    application.include_router(auth_router)
    application.include_router(oauth_router)
    application.include_router(openapi_document_router)
    application.include_router(sessions_router)
    application.include_router(master_router)
    application.include_router(support_router)
