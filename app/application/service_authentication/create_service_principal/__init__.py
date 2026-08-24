"""Create AUTO service principal operation facade."""

from __future__ import annotations

from .command import CreateServicePrincipalCommand
from .handler import CreateServicePrincipalHandler

__all__ = ("CreateServicePrincipalCommand", "CreateServicePrincipalHandler")
