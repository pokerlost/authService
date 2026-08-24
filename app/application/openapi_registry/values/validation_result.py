"""Typed OpenAPI contract validation report."""

from __future__ import annotations

from domain.value_model import ValueModel

from .validation_issue import OpenAPIValidationIssue


class OpenAPIContractValidationResult(ValueModel):
    """Deterministic validation outcome returned to the control plane."""

    valid: bool
    issues: list[OpenAPIValidationIssue]
