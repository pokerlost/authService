"""Semantic validated type facade."""

from __future__ import annotations

from .api_operation_id import APIOperationId, validate_api_operation_id
from .contract_version import ContractVersion, validate_contract_version
from .nickname import Nickname, normalize_nickname
from .password_value import PasswordValue
from .service_id import ServiceId, validate_service_id
from .service_slug import ServiceSlug, validate_service_slug
from .username import Username, canonicalize_username

__all__ = (
    "APIOperationId",
    "ContractVersion",
    "Nickname",
    "PasswordValue",
    "ServiceId",
    "ServiceSlug",
    "Username",
    "canonicalize_username",
    "normalize_nickname",
    "validate_api_operation_id",
    "validate_contract_version",
    "validate_service_id",
    "validate_service_slug",
)
