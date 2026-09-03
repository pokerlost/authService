# Containers and Kubernetes

This page documents the generated Docker image and Helm chart workflows without treating them as
an application deployment system.

## Docker build

The builder resolves the pinned private `pypokerlost` Git source. BuildKit therefore requires an
authorized SSH agent and a trusted GitHub `known_hosts` entry:

```bash
ssh-add -l
ssh-keygen -F github.com
make docker-build
```

`make docker-build` forwards the agent with `--ssh default` and mounts `$HOME/.ssh/known_hosts` as
the `github_known_hosts` build secret. The Dockerfile marks both inputs as required. Do not copy a
private key into the build context, image, `.env`, or chart values, and do not disable host
verification.

The multi-stage image installs build-only Git and SSH tooling in the builder. The Python 3.14
runtime contains the locked application environment, runs as numeric user and group `10001`, and
starts Gunicorn with Uvicorn workers. GitHub credentials are not runtime inputs.

## Helm validation

The chart lives under `deploy/helm/authservice/`. Validate it locally with:

```bash
make helm-lint
make helm-template
```

These targets wrap `helm lint` and `helm template`; they do not install or upgrade a cluster release.

## Runtime configuration and probes

The Deployment exposes the HTTP container port and configures both liveness and readiness probes as `GET /`. The root endpoint does not require a database query, so it checks that the application process can serve its base response without turning the probe into a business operation.

Non-secret environment values come from the `environment` map. Database credentials and the
optional Logfire token use `secretEnvironment` references to existing Kubernetes Secret names and
keys. The stable root and OpenAPI paths and operation IDs are defined in source and do not appear
as Helm configuration. Never place secret values in `environment`, a ConfigMap, a committed values
file, or rendered documentation.

The service-owned `token` values supply the exact issuer and access-token TTL. `jwtSigningKey`
supplies the non-secret key ID, mounted path, existing Secret name, and Secret data key. Only the
selected private-key entry is mounted read-only; PEM material never enters ConfigMap data,
environment values, the image, or committed chart values.

The current chart contains no outbound target, outbound credential, token storage, or retry
values. A future real target may add its base URL and request timeout through the existing
non-secret `environment` or explicit ConfigMap convention. Credential and token-store inputs remain
service-owned and are wired only when an implemented use case needs them; secrets use
`secretEnvironment` and existing Kubernetes Secret references. `PokerlostRetryPolicy` values never
become deployment settings. Authentication material and tokens never become chart values,
ConfigMap data, logs, or rendered manifests. See `docs/architecture/inter-service-clients.md` for the
ownership and lifecycle pattern.

The ClusterIP is an internal target and must remain behind mandatory production HTTPS/TLS
termination. Do not expose the generated HTTP container port directly as a plaintext production
edge. The chart also disables service-account token mounting, requests a non-root runtime, uses a
read-only root filesystem, drops Linux capabilities, and mounts a bounded writable temporary
volume. Review rendered output and environment-specific Secret references before deployment;
successful linting and rendering do not prove cluster readiness or application correctness.
