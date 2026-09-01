# API errors

This page documents the failure categories normalized by the API boundary into safe
`PokerlostResponse[None]` forms.

## Runtime mappings

`AUTHSERVICE` is the generated service error prefix. Application operations use these mappings:

| Source | HTTP status | Error code | Public message |
| --- | --- | --- | --- |
| Request validation | `422` | `AUTHSERVICE_VALIDATION_ERROR` | `Request validation failed` |
| `NotFoundError` | `404` | `AUTHSERVICE_NOT_FOUND` | `Requested resource was not found.` |
| `ConflictError` | `409` | `AUTHSERVICE_CONFLICT` | `Operation conflicts with current state.` |
| `InvalidOperationError` | `422` | `AUTHSERVICE_INVALID_OPERATION` | `Operation is invalid.` |
| `IntegrityError` | `500` | `AUTHSERVICE_INTEGRITY_ERROR` | `Application state is inconsistent.` |
| Base application failure | `500` | `AUTHSERVICE_APPLICATION_ERROR` | `Application operation failed.` |
| PostgreSQL unavailable | `503` | `AUTHSERVICE_DATABASE_UNAVAILABLE` | `Required database is unavailable` |
| Other SQLAlchemy failure | `500` | `AUTHSERVICE_DATABASE_ERROR` | `Database operation failed` |
| Unexpected exception | `500` | `AUTHSERVICE_INTERNAL_ERROR` | `Internal server error` |

Framework HTTP exceptions are also normalized. An unmatched path uses
`AUTHSERVICE_NOT_FOUND` with `Resource not found`; an unsupported method uses
`AUTHSERVICE_METHOD_NOT_ALLOWED` with `Method not allowed`. Other framework HTTP
statuses retain their status and use `AUTHSERVICE_HTTP_ERROR` with
`HTTP request failed`.

## Application failures

Application errors are transport-independent exceptions with stable public codes and messages.
The API layer selects the HTTP status. A concrete service may add a specific application failure
only when its responsibilities require one, then it must publish the corresponding
`PokerlostResponse[None]` status on affected routes and update the
`docs/api/public-surface.md`.

## Database and unexpected failures

An exact driver connection refusal is normalized at the database engine boundary to SQLAlchemy's
availability category and becomes `503`. Other SQLAlchemy failures become sanitized `500`
responses. An exception that escapes the registered handlers is caught by request middleware and
becomes the generic internal `500` response.

Request and correlation identifiers accompany logs and response headers, not the JSON envelope.
Public failures do not expose submitted values, tracebacks, SQL details, credentials, or other
secrets. The envelope invariants are defined in
`docs/api/application-response.md`.

## `getToken` errors

Every handled failure at `POST /getToken` uses `PokerlostResponse[None]`; none exposes FastAPI
`detail`, Pydantic validation details, submitted JSON, credentials, or token values.

| Condition | Application error | HTTP status |
| --- | --- | ---: |
| Missing or malformed JSON envelope or payload | `AUTHSERVICE_INVALID_REQUEST` | `400` |
| Unknown/non-confidential client, rejected secret, disabled client/principal, or no accepted credential | `AUTHSERVICE_INVALID_CLIENT` | `401` |
| Authenticated client without explicit service-client credential permission | `AUTHSERVICE_UNAUTHORIZED_CLIENT` | `400` |
| Empty, unknown, duplicated, or unauthorized requested scope | `AUTHSERVICE_INVALID_SCOPE` | `400` |
| Missing, malformed, or unauthorized logical audience | `AUTHSERVICE_INVALID_TARGET` | `400` |
| PostgreSQL temporarily unavailable | `AUTHSERVICE_TEMPORARILY_UNAVAILABLE` | `503` |
| Unexpected token-processing failure | `AUTHSERVICE_SERVER_ERROR` | `500` |

`AUTHSERVICE_INVALID_CLIENT` uses the same safe message for every credential failure. No response
contains an authentication challenge or retry header. A retry delay, if introduced for an
availability response, belongs only in `PokerlostResponse.retry_after`.
