# Inter-service clients

This page defines the extension pattern for a service with a real outbound protected Pokerlost
dependency. authService currently creates no outbound client, credential state, token store,
refresher, or retry configuration and does not call itself or accountsService.

## Ownership

The SDK owns typed methods and models, `PokerlostClient`, transport, canonical response decoding,
errors, retry middleware, bearer-header injection, and one narrow reactive refresh trigger. The
consuming service owns client credentials, explicit initial `GetToken` orchestration, exact target
audience, a persistent `PokerlostTokenStore`, and a cross-process-safe
`PokerlostTokenRefresher` implementation.

Create one target-specific `PokerlostClient` in lifespan only for a real dependency. Do not create
direct HTTP transport, a string-keyed client registry, or a per-request client.

## Middleware composition

Protected target calls compose:

```text
PokerlostRetryMiddleware
→ PokerlostAuthenticationMiddleware
→ transport
```

Every concrete method explicitly declares `__scopes__`. `None` means no access-token scope
requirement and bypasses token storage, refresh, and header injection. A non-empty tuple chooses
the protected flow. Missing metadata or an empty tuple is a local configuration error before
network I/O.

For a protected call, authentication middleware loads stored state by client identity, exact
audience, and canonical scope set, refreshes once if its aware UTC expiry has passed, and injects
`Authorization: Bearer <access-token>` into the internal transport call. The access token never
enters `PokerlostRequest`.

If the service returns exactly `POKERLOST_ACCESS_TOKEN_EXPIRED`, middleware invalidates or compares
the observed version, invokes the injected refresher once, rebuilds authorization state, and
replays the identical operation/body/business operation ID once. Invalid token, insufficient
scope, arbitrary `401`, and `403` responses do not trigger refresh.

Production refresh coordination uses a bounded lease or equivalent compare-and-swap design. It
must allow stale workers to reload a newer version and must not hold a PostgreSQL transaction while
redeeming a rotating refresh token over the network. Raw access and refresh tokens require an
approved reversible storage primitive and are never persisted in plaintext.

## Retry

Retry is explicit per logical call:

```python
from pypokerlost import PokerlostRequestOptions
from pypokerlost.middleware import PokerlostRetryPolicy

options = PokerlostRequestOptions(
    retry_policy=PokerlostRetryPolicy(),
)
```

The immutable policy uses at most three attempts including the first, full jitter, and a
five-second logical budget. It retries canonical connection/timeout failures and statuses `408`,
`425`, `429`, `500`, `502`, `503`, and `504`. Server delay comes only from body `retry_after` and
must fit the remaining budget. Cancellation propagates immediately. A malformed `502`, `503`, or
`504` can retry by safe status metadata; a malformed ordinary `2xx` is a non-retryable protocol
error.

## Business boundaries

Transport retry is not business idempotency. A replay-safe mutation reuses the same business
operation ID, semantic payload, generated operation, and target. Middleware never creates or
changes those values and does not own workflow persistence or reconciliation.

Never keep a PostgreSQL transaction open during initial token acquisition, refresh, a target call,
retry sleep, or another attempt. Persist short local phases at explicit workflow boundaries.

## Privacy

Never log client secrets, passwords, private keys, access or refresh tokens, login grants,
authorization headers, or raw request/response bodies. Secret-bearing SDK models hide
representations and validation input; canonical exceptions retain only safe scalar metadata.
