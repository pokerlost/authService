"""ASGI runtime entrypoint."""

from __future__ import annotations

from .application import create_application

application = create_application()
