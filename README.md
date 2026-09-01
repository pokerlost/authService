# authService

`authService` is the PokerLost OAuth2 authorization server. It provides PostgreSQL-backed service
principals and confidential clients, operator bootstrap, and short-lived RS256 access tokens for
the OAuth2 `client_credentials` grant.

Read `docs/index.md` for the complete guide and `AGENTS.md` for normative engineering rules.
Python 3.14 or newer is required.

## Install

The mandatory private `pypokerlost` dependency requires GitHub SSH read access. Create local
configuration, verify the SSH identity, and install the locked environment:

```bash
cp .env.example .env
ssh-add -l
ssh -T git@github.com
uv lock
uv sync --locked
```

Replace the local placeholders in `.env`, provide an RSA private key at the configured
`AUTHSERVICE_JWT__PRIVATE_KEY_PATH`, and keep secrets and private keys outside the repository.
See `docs/getting-started/installation.md` and `docs/getting-started/configuration.md` for details.

## Run

```bash
make run
```

## HTTP surface

| method | path | operation_id | response_model |
| --- | --- | --- | --- |
| `GET` | `/` | `auth.getRoot` | `RootResponse` |
| `GET` | `/openapi.get` | `openapi.get` | `OpenAPIResponse` |
| `POST` | `/oauth.token` | `oauth.token` | `ApplicationResponse[OAuthTokenResponse]` |

The base identifiers shown are the `.env.example` values. Every response uses
`ApplicationResponse`. The OAuth2 token operation retains its form and HTTP Basic request
mechanics, while its access token is returned only as `result.access_token`. See
`docs/api/public-surface.md`.

## Bootstrap a service client

Create the service principal, confidential client, exact grants, and first credential in one local
PostgreSQL transaction:

```bash
authservice bootstrap-service-client \
  --service-slug accountsservice \
  --scope auth.internal.provision_human \
  --scope auth.internal.set_principal_status \
  --scope auth.internal.assign_role \
  --scope auth.internal.issue_login_grant \
  --resource urn:pokerlost:service:authService
```

The command prints the generated client ID and raw client secret only after commit. Store the raw
secret immediately; authService persists only its digest and cannot recover it later.

Service consumers use the SDK-owned authentication and outbound middleware facades:

```python
from pypokerlost.client.auth import ClientCredentialsTokenProvider
from pypokerlost.middleware import BearerTokenMiddleware, RetryMiddleware
```

`RetryMiddleware` is registered outside `BearerTokenMiddleware`, but retry stays off unless a
replay-safe call supplies an explicit policy. authService itself creates no outbound client to
accountsService or to itself.

## Development and deployment

Run `make help` for the thin local tool interface. The regular quality entry points are:

```bash
make check
make pre-commit
```

See `docs/development/commands.md` and `docs/development/containers-and-kubernetes.md` for Docker
and Helm workflows.
