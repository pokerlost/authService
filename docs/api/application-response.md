# PokerlostResponse

Every normal authService response uses the canonical five-field
`PokerlostResponse[ResultT]` JSON envelope.

## Success

```json
{
  "ok": true,
  "result": null,
  "error": null,
  "error_message": null,
  "retry_after": null
}
```

`result` is the typed operation result or `null`. Success forbids all failure metadata.

## Failure

```json
{
  "ok": false,
  "result": null,
  "error": "AUTHSERVICE_TEMPORARILY_UNAVAILABLE",
  "error_message": "The token service is temporarily unavailable.",
  "retry_after": 1.5
}
```

Failure requires a stable non-empty `error`, forbids a result, and may include a sanitized message.
`retry_after`, when present, is a finite non-negative number of seconds. It is body data only and
is never mirrored to an HTTP header. Success requires it to be `null`.

The model is strict, immutable, closed to extra fields, and rejects impossible field combinations
through validation rather than assertions. It is the API wire envelope, not an application-layer
Result abstraction.

## Token result

`POST /getToken` returns `PokerlostToken` inside `result`. The token has `access_token`, optional
`refresh_token`, positive `expires_in`, exact immutable `scopes`, and logical `audience`. It has no
Bearer/token-type or HTTP-header representation. The current implemented service flow always
returns `refresh_token: null`.

The client decodes this envelope for both 2xx and non-2xx statuses. A failed envelope becomes a
canonical SDK exception; malformed JSON or an invalid envelope becomes a protocol error. Neither
the server nor SDK exceptions retain raw request or response bodies.
