# Operation contract

This page is the canonical wire contract for public PokerLost API operations implemented by
`authService`.

## System boundary

`GET /` is the sole path exception. Its operation ID comes from the required
`AUTHSERVICE_ROOT_OPERATION` setting. OpenAPI publication uses the required
`AUTHSERVICE_OPENAPI_OPERATION` setting for both its operation ID and its
`"/" + operation_id` path. The generator treats both configured base operations as system
operations and does not generate callable methods for them.

Every operation ID has exactly two segments and one dot:

```text
operation_id = namespace.someOperation
path         = "/" + operation_id
```

The complete accepted operation pattern is:

```text
^[a-z][A-Za-z0-9]*\.[a-z][A-Za-z0-9]*$
```

Each segment starts with a lowercase ASCII letter and otherwise contains only ASCII letters and
digits. Ordinary lowerCamelCase is expected. Underscores, hyphens, extra dots, missing dots, and
uppercase initial characters are invalid. `accounts.confirmLogin` is valid;
`accounts.confirm_login`, `accounts.self.get`, and `Accounts.get` are invalid.

Define one module-level `OPERATION` constant and derive both `path` and `operation_id` from it. The
SDK-compatible HTTP methods are `GET`, `POST`, `PUT`, `PATCH`, and `DELETE`; use `POST` by default
unless the operation semantics require another supported method.

## Application request body

Ordinary PokerLost application input is one named, closed, typed JSON object based on
`RequestModel`. Its component and class name ends in `Request`. Application-owned field names are
alias-free `snake_case` and remain unchanged during serialization.

Operation input does not use OpenAPI path, query, header, or cookie parameters. Do not use an
embedded body, an anonymous inline object, or a free-form top-level body. A `GET` operation that
has input still receives a JSON body. A parameterless operation omits `requestBody` completely
instead of publishing an empty object.

## Application response schemas

A successful operation publishes `ApplicationResponse[<SemanticName>Response]`. Every expected
handled 4xx or 5xx response publishes `ApplicationResponse[None]`; an operation with a request body
also publishes that model for validation status `422`. All numeric 2xx responses for one operation
must use compatible JSON schemas.

The envelope fields and invariants belong to `docs/api/application-response.md`, and runtime
failure mappings belong to `docs/api/errors.md`.

## OAuth2 token request mechanics

`POST /oauth.token` retains the canonical operation ID and matching path. Its request follows the
OAuth2 form protocol rather than the PokerLost application JSON-body rule. It accepts
`application/x-www-form-urlencoded` with exactly one `grant_type`, `scope`, and `resource` field.
Confidential-client authentication is an HTTP Basic security dependency. The body must not contain
`client_id` or `client_secret`.

The response follows the universal PokerLost rule: success is
`ApplicationResponse[OAuthTokenResponse]`, and every handled failure is
`ApplicationResponse[None]`. Validation is normalized to a stable authService application error
instead of exposing FastAPI `detail` or Pydantic details. FastAPI generates the form media type and
HTTP Basic security declaration from the concrete route dependencies; the OpenAPI wrapper does not
rewrite them.

## Service-specific security

When a concrete service requires authorization, declare it through that service's FastAPI security
dependencies. It must not alter the operation, path, application-input, or response-envelope rules.
FastAPI-generated security metadata remains service-specific and is preserved by the OpenAPI
publication described in `docs/api/openapi-and-sdk.md`.

## Contract changes

An API change must update `docs/api/public-surface.md`, this page when the operation rules change,
and the relevant response or publication page. A wire-contract change also requires the
authoritative `pypokerlost` compatibility workflow.
