"""
Core views — healthcheck endpoint for Docker / Kubernetes probes.
"""
from django.db import connection
from django.http import JsonResponse


def healthz(request):
    """Healthcheck endpoint. Returns 200 + {"status": "ok"} if DB is reachable."""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        return JsonResponse({"status": "ok"})
    except Exception as exc:
        return JsonResponse({"status": "error", "detail": str(exc)}, status=503)
