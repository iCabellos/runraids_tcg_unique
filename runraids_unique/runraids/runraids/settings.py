"""
Django settings for runraids project.

Generado con Django 5.1.6 y adaptado para despliegue en Vercel + Supabase.
"""

import os
from pathlib import Path

# dj_database_url es opcional: si no está instalado, hacemos fallback a SQLite
try:
    import dj_database_url  # type: ignore
except ImportError:  # pragma: no cover
    dj_database_url = None  # noqa

# --- Paths base ---
BASE_DIR = Path(__file__).resolve().parent.parent

# --- Seguridad / entorno ---
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-no-seguro")
DEBUG = os.getenv("DEBUG", "false").lower() == "true"

# Hosts permitidos (incluye dominios Vercel)
ALLOWED_HOSTS = [".vercel.app", "localhost", "127.0.0.1"]
_extra_hosts = os.getenv("ALLOWED_HOSTS", "").strip()
if _extra_hosts:
    ALLOWED_HOSTS.extend([h.strip() for h in _extra_hosts.split(",") if h.strip()])

# Orígenes de confianza para CSRF (Vercel y opcionales por env, separados por comas)
CSRF_TRUSTED_ORIGINS = ["https://*.vercel.app"]
_extra_csrf = os.getenv("CSRF_TRUSTED_ORIGINS", "").strip()
if _extra_csrf:
    CSRF_TRUSTED_ORIGINS.extend([o.strip() for o in _extra_csrf.split(",") if o.strip()])

# --- Aplicaciones ---
INSTALLED_APPS = [
    # Django
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Apps propias
    "runraids",
    "core",
]

# --- Middleware ---
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    # Whitenoise para servir estáticos en Vercel / WSGI
    "whitenoise.middleware.WhiteNoiseMiddleware",

    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "runraids.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],  # Añade rutas si tienes plantillas globales
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "runraids.wsgi.application"

# --- Base de datos ---
# En Vercel/Supabase: usa DATABASE_URL (Transaction Pooler con sslmode=require)
# En local: si no hay DATABASE_URL o falta dj_database_url -> SQLite
_database_url = os.getenv("DATABASE_URL", "").strip()
if _database_url and dj_database_url:
    DATABASES = {
        "default": dj_database_url.config(
            default=_database_url,
            conn_max_age=600,
            ssl_require=True,
        )
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

# --- Validación de contraseñas ---
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# --- Internacionalización ---
LANGUAGE_CODE = "es-es"
TIME_ZONE = os.getenv("TIME_ZONE", "Europe/Madrid")
USE_I18N = True
USE_TZ = True

# --- Archivos estáticos / media ---
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# Whitenoise: comprimir y versionar estáticos
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# --- Primary key por defecto ---
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# --- Seguridad extra en producción ---
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_SSL_REDIRECT = os.getenv("SECURE_SSL_REDIRECT", "true").lower() == "true"
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

# --- Logging básico (útil para depurar en Vercel) ---
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "root": {"handlers": ["console"], "level": os.getenv("LOG_LEVEL", "INFO")},
}
