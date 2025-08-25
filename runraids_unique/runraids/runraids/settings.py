"""
Django settings for runraids project.

Generado con Django 5.1.6 y adaptado para despliegue en Vercel + Supabase.
"""

import os
from pathlib import Path

# dj_database_url para parsear DATABASE_URL
try:
    import dj_database_url  # type: ignore
except ImportError:  # pragma: no cover
    dj_database_url = None  # noqa

BASE_DIR = Path(__file__).resolve().parent.parent

# --- Seguridad / entorno ---
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-no-seguro")
DEBUG = os.getenv("DEBUG", "false").lower() == "true"

# Detectar entorno Vercel
ON_VERCEL = os.getenv("VERCEL", "") not in ("", "0", "false", "False")

# Hosts / CSRF
ALLOWED_HOSTS = [".vercel.app", "localhost", "127.0.0.1"]
_extra_hosts = os.getenv("ALLOWED_HOSTS", "").strip()
if _extra_hosts:
    ALLOWED_HOSTS.extend([h.strip() for h in _extra_hosts.split(",") if h.strip()])

CSRF_TRUSTED_ORIGINS = ["https://*.vercel.app"]
_extra_csrf = os.getenv("CSRF_TRUSTED_ORIGINS", "").strip()
if _extra_csrf:
    CSRF_TRUSTED_ORIGINS.extend([o.strip() for o in _extra_csrf.split(",") if o.strip()])

# --- Apps ---
INSTALLED_APPS = [
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
        "DIRS": [],
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

# =========================
#        BASE DE DATOS
# =========================

# 1) Intentar leer DATABASE_URL directamente
DATABASE_URL = os.getenv("DATABASE_URL", "").strip()

# 2) Si está vacío, reconstruirlo desde las piezas (evita depender de la interpolación de Vercel)
if not DATABASE_URL:
    db_user = os.getenv("DB_USER", "").strip()
    db_password = os.getenv("DB_PASSWORD", "").strip()
    db_host = os.getenv("DB_HOST", "").strip()
    db_port = os.getenv("DB_PORT", "").strip()
    db_name = os.getenv("DB_NAME", "").strip()
    if all([db_user, db_password, db_host, db_port, db_name]):
        DATABASE_URL = f"postgres://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}?sslmode=require"

# 3) Lógica final:
#    - En Vercel o en producción (DEBUG=False) exigimos Postgres (sin SQLite).
#    - En local con DEBUG=True, si no hay DATABASE_URL, usamos SQLite por comodidad.
if (ON_VERCEL or not DEBUG):
    if not DATABASE_URL:
        raise RuntimeError(
            "DATABASE_URL es obligatorio en Vercel/producción. "
            "Configúralo (Transaction Pooler de Supabase con ?sslmode=require)."
        )
    if not dj_database_url:
        raise RuntimeError("dj-database-url debe estar instalado en Vercel/producción.")
    DATABASES = {
        "default": dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600,
            ssl_require=True,
        )
    }
else:
    if DATABASE_URL and dj_database_url:
        DATABASES = {
            "default": dj_database_url.config(
                default=DATABASE_URL,
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

# --- Estáticos / media ---
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# --- Seguridad extra en producción ---
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_SSL_REDIRECT = os.getenv("SECURE_SSL_REDIRECT", "true").lower() == "true"
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

# --- Logging a consola (útil en Vercel) ---
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "root": {"handlers": ["console"], "level": os.getenv("LOG_LEVEL", "INFO")},
}
