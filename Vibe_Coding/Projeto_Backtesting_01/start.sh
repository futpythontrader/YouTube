#!/usr/bin/env bash
set -euo pipefail

echo "→ Aplicando migrations..."
python manage.py migrate --noinput

echo "→ Iniciando Gunicorn em :${PORT:-8000}"
exec gunicorn config.wsgi:application \
    --bind "0.0.0.0:${PORT:-8000}" \
    --workers "${WEB_CONCURRENCY:-3}" \
    --threads "${WEB_THREADS:-2}" \
    --timeout 60 \
    --access-logfile - \
    --error-logfile -
