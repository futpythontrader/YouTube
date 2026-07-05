"""
Django production settings for Docker / EasyPanel deploy.

Usage: DJANGO_SETTINGS_MODULE=config.settings.production
"""
from .base import *  # noqa: F401, F403

# =============================================================================
# Security
# =============================================================================
DEBUG = False

ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="*", cast=Csv())  # noqa: F405

# HTTPS / proxy headers (EasyPanel uses a reverse proxy)
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = config("SECURE_SSL_REDIRECT", default=True, cast=bool)  # noqa: F405

# =============================================================================
# Database (PostgreSQL via DATABASE_URL)
# =============================================================================
import dj_database_url  # noqa: E402

DATABASE_URL = config("DATABASE_URL", default="sqlite:///db.sqlite3")  # noqa: F405
DATABASES = {
    "default": dj_database_url.parse(DATABASE_URL, conn_max_age=600),
}

# =============================================================================
# Static files (Whitenoise)
# =============================================================================
# Whitenoise middleware must be right after SecurityMiddleware
MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")  # noqa: F405

STATIC_ROOT = BASE_DIR / "staticfiles"  # noqa: F405
STATIC_URL = "static/"

STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# =============================================================================
# Email (SMTP)
# =============================================================================
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = config("EMAIL_HOST", default="smtp.gmail.com")  # noqa: F405
EMAIL_PORT = config("EMAIL_PORT", default=587, cast=int)  # noqa: F405
EMAIL_USE_TLS = True
EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="")  # noqa: F405
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="")  # noqa: F405
DEFAULT_FROM_EMAIL = config("DEFAULT_FROM_EMAIL", default="noreply@backtestbet.com")  # noqa: F405

# =============================================================================
# Celery (future — disabled for MVP)
# =============================================================================
# CELERY_BROKER_URL = config("CELERY_BROKER_URL", default="")
# CELERY_RESULT_BACKEND = config("CELERY_RESULT_BACKEND", default="")

# =============================================================================
# Logging
# =============================================================================
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {
            "format": "{levelname} {asctime} {module} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "WARNING",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "apps": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}
