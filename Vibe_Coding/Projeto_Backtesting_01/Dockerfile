# syntax=docker/dockerfile:1.7
ARG PYTHON_VERSION=3.13-slim

# ============= BASE =============
FROM python:${PYTHON_VERSION} AS base
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PORT=8000
WORKDIR /app

# ============= BUILDER =============
FROM base AS builder
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip wheel --wheel-dir /wheels -r requirements.txt

# ============= RUNTIME =============
FROM base AS runtime
RUN apt-get update && apt-get install -y --no-install-recommends \
        libpq5 \
        curl \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd -r app && useradd -r -g app app

COPY --from=builder /wheels /wheels
RUN pip install --no-index --find-links=/wheels /wheels/* && rm -rf /wheels

COPY --chown=app:app . .

# Collect static files at build time
ENV DJANGO_SETTINGS_MODULE=config.settings.production \
    SECRET_KEY=build-time-only-not-used-at-runtime \
    DATABASE_URL=sqlite:///tmp/build_dummy.db
RUN python manage.py collectstatic --noinput && \
    rm -f /tmp/build_dummy.db

USER app
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD curl -fsS "http://localhost:${PORT}/healthz/" || exit 1

CMD ["./start.sh"]
