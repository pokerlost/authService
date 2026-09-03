# Header authorization

Protected Pokerlost operations receive an access token only through the standard HTTP
`Authorization: Bearer <access-token>` header and authorize solely through exact scopes.

## Request boundary

Every business request body remains a pure `PokerlostRequest[Payload]` JSON envelope. It contains
no access token, authorization object, headers map, method binding, or middleware metadata. Public
operations send no access-token header.

`getToken` is public with respect to access-token authorization. Its typed request payload still
contains OAuth client credentials because exchanging those credentials is the operation itself.

## Local verifier seam

`app/application/ports/pokerlost_token_verifier.py` defines the framework-independent
`PokerlostTokenVerifier` port. `app/api/dependencies/authorization.py` uses FastAPI's standard
OAuth2 client-credentials scheme with `auto_error=False`, parses the bearer header, and asks the
verifier to validate it for the exact `authService` audience. It then requires every route scope
before handler execution.

authService currently implements no protected business route, so production composition does not
install a concrete verifier. The dependency is ready for the first real protected operation; no
placeholder endpoint or fake verifier is added merely to expose a scheme.

## Route composition

```python
from typing import Annotated

from fastapi import APIRouter, Security
from pypokerlost.types import (
    PokerlostAuthorizationContext,
    PokerlostRequest,
    PokerlostResponse,
)

from api.dependencies import authorize_pokerlost_request
from domain.enums import Scopes

router = APIRouter(tags=["principals"])


@router.post(
    path="/replacePrincipalScopes",
    operation_id="replacePrincipalScopes",
    response_model=PokerlostResponse[ReplacePrincipalScopesResponse],
)
async def replace_principal_scopes(
    request: PokerlostRequest[ReplacePrincipalScopesRequest],
    authorization: Annotated[
        PokerlostAuthorizationContext,
        Security(
            authorize_pokerlost_request,
            scopes=[Scopes.INTERNAL_REPLACE_PRINCIPAL_SCOPES],
        ),
    ],
) -> dict[str, object]: ...
```

The example documents composition only; a real endpoint maps its application result to a plain
mapping and lets `response_model` validate and serialize it. `replacePrincipalScopes` is an honest
SDK stub and is not an implemented authService route at this stage.

## Failure contract

Missing or malformed authorization maps to `POKERLOST_AUTHENTICATION_REQUIRED`, invalid token or
audience to `POKERLOST_ACCESS_TOKEN_INVALID`, expiry to `POKERLOST_ACCESS_TOKEN_EXPIRED`, and a
missing exact scope to `POKERLOST_INSUFFICIENT_SCOPE`. Central exception handlers serialize all of
them as `PokerlostResponse[None]`; FastAPI's default `detail` body is never exposed.

The expiry error occurs in the dependency before handler entry. This invariant allows SDK
authentication middleware to invoke one injected refresh adapter and replay the original request
once without duplicating business side effects.

## Scope and OpenAPI contract

The only local catalog is `app/domain/enums/scopes.py::Scopes`. Its values are stable dotted
lowerCamelCase capabilities and its description mapping feeds the standard `PokerlostOAuth2`
OpenAPI scheme. Every protected route supplies a non-empty exact scope list through `Security`; an
empty list is a configuration error.

Standard OpenAPI is the only generator source:

```text
local Scopes and route Security requirement
→ standard OpenAPI security metadata
→ generator validation against explicit SDK PokerlostScopes
→ method.__scopes__
```

No security requirement means `method.__scopes__ is None`. A protected method has a non-empty
tuple of `PokerlostScopes`; an empty or missing declaration is invalid before network I/O. A
document with no protected operations may omit `components.securitySchemes` entirely.
