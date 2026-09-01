# authService

`authService` is the Pokerlost token authority. It provides PostgreSQL-backed service principals
and confidential clients, operator bootstrap, and short-lived RS256 access tokens through the
private body-only Pokerlost JSON protocol over HTTPS.

Read `docs/index.md` for the complete guide and `AGENTS.md` for normative engineering rules. Python
3.14 or newer is required.

## Install

The mandatory private `pypokerlost` dependency requires GitHub SSH read access:

```bash
cp .env.example .env
ssh-add -l
ssh -T git@github.com
uv lock
uv sync --locked
```

Replace local placeholders in `.env`, provide an RSA private key at the configured
`AUTHSERVICE_JWT__PRIVATE_KEY_PATH`, and never store secrets or private keys in the repository.

## Run

```bash
make run
```

## HTTP surface

| method | path | operation_id | response |
| --- | --- | --- | --- |
| `GET` | `/` | `getRoot` | `PokerlostResponse[None]` |
| `GET` | `/getOpenApi` | `getOpenApi` | `PokerlostResponse[dict[str, JSONValue]]` |
| `POST` | `/getToken` | `getToken` | `PokerlostResponse[PokerlostToken]` |

The infrastructure endpoints accept no body or authentication. `getToken` receives client
credentials, exact scopes, and a logical target audience only in `PokerlostRequest.payload`; it
accepts no authentication header, cookie, query parameter, or form data.

## Bootstrap a service client

Create one service principal, confidential client, exact grants, and first credential in a local
PostgreSQL transaction:

```bash
authservice bootstrap-service-client \
  --service-slug accountsservice \
  --scope auth.internal.provisionHuman \
  --scope auth.internal.setPrincipalStatus \
  --scope auth.internal.assignPrincipalRole \
  --scope auth.internal.issueLoginGrant \
  --resource urn:pokerlost:service:authService
```

The command prints the generated client ID and raw secret only after commit. Store that secret
immediately; authService persists only its digest. authService creates no outbound client to
itself or accountsService. See `docs/api/public-surface.md` and
`docs/architecture/service-client-credentials.md`.

## Development and deployment

Run `make help` for the local tool interface. Regular quality entry points are:

```bash
make check
make pre-commit
```

Production access requires HTTPS/TLS. The generated Helm ClusterIP is an internal target and must
remain behind trusted TLS termination.
