"""OpenAPI registry error facade."""

from __future__ import annotations

from .activation_conflict import OpenAPIContractActivationConflictError
from .contract_not_found import OpenAPIContractNotFoundError
from .not_validated import OpenAPIContractNotValidatedError
from .operation_id_conflict import OpenAPIOperationIDConflictError
from .registered_service_not_found import RegisteredServiceNotFoundError
from .registration_invalid import OpenAPIContractRegistrationInvalidError
from .security_ack_required import OpenAPIContractSecurityAcknowledgementRequiredError
from .version_conflict import OpenAPIContractVersionConflictError

__all__ = (
    "OpenAPIContractActivationConflictError",
    "OpenAPIContractNotFoundError",
    "OpenAPIContractNotValidatedError",
    "OpenAPIContractRegistrationInvalidError",
    "OpenAPIContractSecurityAcknowledgementRequiredError",
    "OpenAPIContractVersionConflictError",
    "OpenAPIOperationIDConflictError",
    "RegisteredServiceNotFoundError",
)
