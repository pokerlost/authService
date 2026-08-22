"""Gunicorn production process configuration."""

from __future__ import annotations

import os


def _positive_integer(name: str, default: int) -> int:
    raw_value = os.environ.get(name, str(default))
    try:
        value = int(raw_value)
    except ValueError as exception:
        raise RuntimeError(f"{name} must be an integer") from exception
    if value < 1:
        raise RuntimeError(f"{name} must be greater than zero")
    return value


bind_host = os.environ.get("AUTH_HTTP__HOST", "0.0.0.0")
bind_port = _positive_integer("AUTH_HTTP__PORT", 8000)
bind = f"{bind_host}:{bind_port}"
workers = _positive_integer("GUNICORN_WORKERS", 2)
worker_class = "uvicorn_worker.UvicornWorker"
timeout = _positive_integer("GUNICORN_TIMEOUT", 30)
graceful_timeout = _positive_integer("GUNICORN_GRACEFUL_TIMEOUT", 30)
keepalive = _positive_integer("GUNICORN_KEEPALIVE", 5)
forwarded_allow_ips = os.environ.get("GUNICORN_FORWARDED_ALLOW_IPS", "127.0.0.1")
accesslog = "-"
errorlog = "-"
capture_output = True
worker_tmp_dir = "/tmp"
