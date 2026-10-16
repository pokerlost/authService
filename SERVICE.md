# authService

`authService` is the proposed authority for Pokerlost principals, exact grants and access tokens. The present checkout is a **service foundation**, not an implemented token API.

## 🧭 Foundation available

The current `serviceTemplate` supplies FastAPI composition, typed settings, safe Pokerlost errors, optional bearer-verifier port, PostgreSQL engine/session ownership, Alembic, logging, Docker and Helm. `GET /`, `GET /getOpenApi`, and health probes are the only routes. The scope catalog is empty. No client/principal entity, token signer, `getToken` handler, operator bootstrap, private-key requirement, protected route or outbound SDK client is active.

The committed `serviceTemplate` source has been applied to `src/authService/` after the earlier foundation cleanup. Project-owned rules, the empty exact scope catalog, and historical revisions were preserved; the five revision files moved byte-for-byte into `migrations/versions/`. This file migration is local and is not a release or a database upgrade. The retired flat `app/` implementation remains recoverable from the prior local commit and private backup.

Earlier Alembic revisions remain immutable historical artifacts. They may create authorization tables on a fresh database even though current ORM metadata is empty. Do not autogenerate a drop migration or run an upgrade against production as part of this cleanup. No live database was accessed.

## 📦 Planned ownership

A later reviewed stage may own service and human principals, confidential clients, direct exact scope/audience grants, one-time login grants, sessions, refresh families and revocation. It may expose `POST /getToken` and other operations only after their complete persistence, authorization, key management, failure and compatibility contracts exist. Current `pypokerlost` methods and scopes remain future-facing SDK contracts, not evidence of server endpoints.

`accountsService` owns usernames, nicknames and password hashes. `authService` must not read that database or implement password verification. Other services validate short-lived access tokens locally rather than call authService for every request. No shared database access, wildcard grant, identity-category bypass or allow-all authorization is installed.

## 🔒 Deferred token rules

These are requirements for a future token implementation, **not current runtime behavior**:

- Client credentials are accepted only in a typed `getToken` JSON payload, stored as a digest, and never logged.
- Issuance requires the exact intersection of active principal/client scope and audience grants. Claims use one exact service audience; no wildcard or implicit category authority.
- The prior candidate used short-lived RS256 tokens with a key of at least 2048 bits and a `kid`; signing material stays outside source and is never copied into an image. Revalidate the policy at implementation time. No PyJWT dependency or key mount is present now.
- A public token operation does not accept an access-token bearer header as a substitute for its own client credentials. Future refresh, JWKS, session and revocation routes remain separate stages.

See the [current public surface](docs/api/public-surface.md) and [planned credential flow](docs/architecture/service-client-credentials.md). The private backup records removed code and configuration; it is not a database rollback plan.
