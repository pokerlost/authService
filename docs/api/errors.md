# API errors

Central handlers serialize all supported failures as `PokerlostResponse[None]` without raw input or
internal state.

## Runtime mappings

| Source | Status | Stable error |
| --- | --- | --- |
| Missing/malformed body authentication | `401` | `AUTHENTICATION_REQUIRED` |
| Invalid access token or audience | `401` | `INVALID_ACCESS_TOKEN` |
| Missing exact scope | `403` | `INSUFFICIENT_SCOPE` |
| Request validation | `422` | `AUTHSERVICE_VALIDATION_ERROR` |
| Application not found | `404` | `AUTHSERVICE_NOT_FOUND` |
| Application conflict | `409` | `AUTHSERVICE_CONFLICT` |
| Invalid application operation | `422` | `AUTHSERVICE_INVALID_OPERATION` |
| PostgreSQL unavailable | `503` | `AUTHSERVICE_DATABASE_UNAVAILABLE` |
| Other database failure | `500` | `AUTHSERVICE_DATABASE_ERROR` |
| Unexpected failure | `500` | `AUTHSERVICE_INTERNAL_ERROR` |

Framework not-found and method failures are also normalized. Public messages are fixed sanitized
text. Validation errors never echo submitted values.

An unavailable required verifier is a composition error and fails closed as an internal failure.
Concrete verifier adapters map rejected tokens to `InvalidAccessTokenError`; unexpected verifier
failures remain internal instead of being mislabeled as caller failures.

`retry_after` is null unless a handler has an explicit safe retry delay. No retry guidance is
encoded outside the JSON envelope.

## getToken failures

Every handled failure at `POST /getToken` uses `PokerlostResponse[None]` and omits submitted JSON,
credentials, and token values.

| Condition | Error | Status |
| --- | --- | ---: |
| Missing or malformed envelope/payload | `AUTHSERVICE_INVALID_REQUEST` | `400` |
| Rejected client identity or credential | `AUTHSERVICE_INVALID_CLIENT` | `401` |
| Client lacks service-client credential permission | `AUTHSERVICE_UNAUTHORIZED_CLIENT` | `400` |
| Invalid or unauthorized exact scope | `AUTHSERVICE_INVALID_SCOPE` | `400` |
| Invalid or unauthorized logical audience | `AUTHSERVICE_INVALID_TARGET` | `400` |
| PostgreSQL temporarily unavailable | `AUTHSERVICE_TEMPORARILY_UNAVAILABLE` | `503` |
| Unexpected token-processing failure | `AUTHSERVICE_SERVER_ERROR` | `500` |

Credential failures share one safe public message. Any retry delay is carried only by the body
envelope.
