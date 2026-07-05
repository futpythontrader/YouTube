---
description: "Docker + EasyPanel — Dockerfile multi-stage, docker-compose, deploy em VPS via EasyPanel. Inclui Gunicorn, Whitenoise, Celery worker/beat, healthcheck."
mode: subagent
permission:
  read: allow
  edit: allow
  glob: allow
  grep: allow
  list: allow
  bash: allow
  webfetch: deny
  task: allow
---

# Docker Deploy Python

> Todo projeto entrega Dockerfile + docker-compose prontos para EasyPanel desde o dia 1.

---

## 📦 Entregáveis Obrigatórios

- `Dockerfile` multi-stage otimizado
- `docker-compose.yml` (web + worker + beat opcional)
- `.dockerignore`
- `.env.example` documentado
- `DEPLOY.md` com passo-a-passo do EasyPanel
- `start.sh` (script de boot)
- Endpoint `/healthz/` ativo

---

## 🐳 Dockerfile (Django + Python 3.12)

```dockerfile
# syntax=docker/dockerfile:1.7
ARG PYTHON_VERSION=3.12-slim

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

COPY pyproject.toml requirements.txt* ./
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

# Coleta estáticos no build
ENV DJANGO_SETTINGS_MODULE=config.settings.production \
    SECRET_KEY=build-time-only \
    DATABASE_URL=sqlite:///tmp/build.db
RUN python manage.py collectstatic --noinput

USER app
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD curl -fsS http://localhost:${PORT}/healthz/ || exit 1

CMD ["./start.sh"]
```

---

## 🚦 `start.sh`

```bash
#!/usr/bin/env bash
set -euo pipefail

echo "→ Aplicando migrations..."
python manage.py migrate --noinput

echo "→ Iniciando Gunicorn em :${PORT:-8000}"
exec gunicorn config.wsgi:application \
    --bind 0.0.0.0:${PORT:-8000} \
    --workers ${WEB_CONCURRENCY:-3} \
    --threads ${WEB_THREADS:-2} \
    --timeout 60 \
    --access-logfile - \
    --error-logfile -
```

> Marcar como executável: `chmod +x start.sh`

---

## 🧩 `docker-compose.yml` (EasyPanel)

```yaml
services:
  web:
    build: .
    image: ${IMAGE_NAME:-myapp}:latest
    restart: unless-stopped
    env_file: .env
    ports:
      - "8000:8000"
    healthcheck:
      test: ["CMD", "curl", "-fsS", "http://localhost:8000/healthz/"]
      interval: 30s
      timeout: 5s
      retries: 3

  worker:
    build: .
    image: ${IMAGE_NAME:-myapp}:latest
    restart: unless-stopped
    env_file: .env
    command: celery -A config worker -l info --concurrency=2
    depends_on:
      - redis

  beat:
    build: .
    image: ${IMAGE_NAME:-myapp}:latest
    restart: unless-stopped
    env_file: .env
    command: celery -A config beat -l info
    depends_on:
      - redis

  redis:
    image: redis:7-alpine
    restart: unless-stopped
    volumes:
      - redis_data:/data

volumes:
  redis_data:
```

> **Postgres não está no compose** — usamos a instância da VPS via `DATABASE_URL`.

---

## 🩺 Healthcheck

```python
# apps/core/views.py
from django.db import connection
from django.http import JsonResponse


def healthz(request):
    try:
        with connection.cursor() as c:
            c.execute("SELECT 1")
        return JsonResponse({"status": "ok"})
    except Exception as e:  # pragma: no cover
        return JsonResponse({"status": "error", "detail": str(e)}, status=503)
```

```python
# config/urls.py
from apps.core.views import healthz
urlpatterns += [path("healthz/", healthz, name="healthz")]
```

---

## 📂 `.dockerignore`

```
.git
.gitignore
.env
.env.*
!.env.example
__pycache__
*.pyc
*.pyo
.pytest_cache
.mypy_cache
.coverage
htmlcov/
node_modules
.vscode
.idea
README.md
DEPLOY.md
docs/
tests/
*.sqlite3
media/
```

---

## 🔑 `generate_env.py` — Gerar `.env` automaticamente

Todo projeto deve incluir este script na raiz. Ele copia `.env.example` para `.env` e **gera uma `SECRET_KEY` segura automaticamente**.

```python
#!/usr/bin/env python3
"""Gera o arquivo .env a partir do .env.example com SECRET_KEY aleatória."""
import secrets
import shutil
from pathlib import Path

ENV_EXAMPLE = Path(".env.example")
ENV_FILE = Path(".env")


def generate_secret_key(length: int = 50) -> str:
    return secrets.token_urlsafe(length)


def main() -> None:
    if not ENV_EXAMPLE.exists():
        print("❌ .env.example não encontrado.")
        raise SystemExit(1)

    if ENV_FILE.exists():
        print("⚠️  .env já existe. Abortando para não sobrescrever.")
        print("   Delete-o manualmente se quiser regenerar.")
        raise SystemExit(0)

    shutil.copy(ENV_EXAMPLE, ENV_FILE)

    content = ENV_FILE.read_text()
    secret = generate_secret_key()
    content = content.replace("SECRET_KEY=change-me", f"SECRET_KEY={secret}")
    ENV_FILE.write_text(content)

    print("✅ .env criado com sucesso!")
    print(f"   SECRET_KEY gerada: {secret[:10]}...")
    print("   Preencha as demais variáveis antes de rodar o projeto.")


if __name__ == "__main__":
    main()
```

Uso:
```bash
python generate_env.py
```

> Adicione `generate_env.py` ao `.gitignore`? **Não** — ele é seguro para commitar (não grava secrets no código). Adicione apenas `.env` ao `.gitignore`.

---

## ⚙️ `.env.example`

```env
# === Django ===
SECRET_KEY=change-me
DEBUG=False
ALLOWED_HOSTS=meuapp.com,www.meuapp.com
DJANGO_SETTINGS_MODULE=config.settings.production

# === Banco PostgreSQL (VPS remoto) ===
DATABASE_URL=postgres://user:pass@vps.exemplo.com:5432/myapp_prod?sslmode=require

# === Email SMTP (Gmail App Password) ===
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=seuemail@gmail.com
EMAIL_HOST_PASSWORD=app_password_16_chars
DEFAULT_FROM_EMAIL=App <seuemail@gmail.com>

# === Celery / Redis ===
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/1

# === Mercado Pago (se aplicável) ===
MP_ACCESS_TOKEN=
MP_PUBLIC_KEY=
MP_WEBHOOK_SECRET=

# === Gunicorn ===
WEB_CONCURRENCY=3
WEB_THREADS=2
```

---

## 📘 `DEPLOY.md` — Passo-a-passo EasyPanel

```markdown
# Deploy no EasyPanel

## Pré-requisitos
- VPS com EasyPanel instalado
- PostgreSQL rodando na VPS (ou em outra)
- Domínio apontando para a VPS
- Conta Gmail com App Password gerado

## Passos

### 1. Criar databases no Postgres
```sql
CREATE DATABASE myapp_dev;
CREATE DATABASE myapp_prod;
```

### 2. Criar projeto no EasyPanel
- Tipo: **App**
- Source: **Docker Compose** (cole o `docker-compose.yml`) ou **GitHub** (link do repo + branch `main`)

### 3. Configurar variáveis de ambiente
Cole as do `.env.example` preenchidas. Dica: `python -c "import secrets; print(secrets.token_urlsafe(50))"` para `SECRET_KEY`.

### 4. Configurar domínio
Em **Domains**, adicione `meuapp.com` apontando para a porta 8000 do serviço `web`. EasyPanel emite SSL via Let's Encrypt automaticamente.

### 5. Deploy
Clique **Deploy**. Acompanhe os logs até `Listening at http://0.0.0.0:8000`.

### 6. Criar superuser
Abra o terminal do container `web`:
```bash
python manage.py createsuperuser
```

### 7. Validar
- Acesse `https://meuapp.com/healthz/` → `{"status":"ok"}`
- Acesse `/painel-admin/` → login do superuser
- Faça signup em `/accounts/signup/` → recebe email
```

---

## ✅ Checklist Pré-Deploy

- [ ] `python generate_env.py` executado (`.env` gerado com `SECRET_KEY` real)
- [ ] `DEBUG=False`
- [ ] `ALLOWED_HOSTS` definido
- [ ] `SECRET_KEY` única e secreta
- [ ] `SECURE_SSL_REDIRECT=True` em produção
- [ ] `SECURE_PROXY_SSL_HEADER` configurado (EasyPanel usa proxy)
- [ ] `collectstatic` rodando no build
- [ ] Whitenoise no MIDDLEWARE
- [ ] Healthcheck `/healthz/` responde 200
- [ ] Container roda sem root (USER app)
- [ ] `.env` no `.dockerignore` e `.gitignore`

---

## 🚫 Não Fazer

- ❌ Postgres no compose (sempre VPS remoto)
- ❌ `DEBUG=True` em prod
- ❌ Subir container como root
- ❌ Hardcode de secrets na imagem
- ❌ `ALLOWED_HOSTS=['*']`
