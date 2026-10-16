# syntax=docker/dockerfile:1

FROM ghcr.io/astral-sh/uv:0.12.5 AS uv

FROM python:3.14-slim-bookworm AS builder

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=0

WORKDIR /service

RUN apt-get update \
    && apt-get install --yes --no-install-recommends git openssh-client \
    && rm -rf /var/lib/apt/lists/*

COPY --from=uv /uv /uvx /bin/
RUN install -d -m 0700 /root/.ssh

COPY pyproject.toml uv.lock README.md ./
RUN --mount=type=ssh,required=true \
    --mount=type=secret,id=github_known_hosts,target=/root/.ssh/known_hosts,required=true \
    --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev --no-install-project

COPY src ./src
RUN --mount=type=ssh,required=true \
    --mount=type=secret,id=github_known_hosts,target=/root/.ssh/known_hosts,required=true \
    --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev --no-editable

FROM python:3.14-slim-bookworm AS runtime

LABEL org.opencontainers.image.title="authService" \
    org.opencontainers.image.version="0.1.0"

ENV PATH=/service/.venv/bin:$PATH \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /service

RUN groupadd --gid 10001 service \
    && useradd --uid 10001 --gid service --no-create-home --shell /usr/sbin/nologin service

COPY --from=builder /service/.venv /service/.venv
COPY migrations ./migrations
COPY alembic.ini ./

USER 10001:10001

EXPOSE 8000

CMD ["uvicorn", "authService.app:createApp", "--factory", "--host", "0.0.0.0", "--port", "8000"]
