"""
Django settings for runraids project.

Adaptado para Vercel + Supabase (Transaction Pooler). Sin fallback a SQLite.
"""

import os
from pathlib import Path
from decouple import config

# --- Librería para parsear DATABASE_URL ---
try:
    import dj_database_url  # type: ignore
except ImportError:
    dj_database_url = None

BASE_DIR = Path(__file__).resolve().parent.parent

# Lee primero .env.local si existe
from decouple import Config, RepositoryEnv
env_file = BASE_DIR / ".env.local"
if env_file.exists():
    env = Config(RepositoryEnv(str(env_file)))
else:
    env = config

# =========
# Seguridad
# =========
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-no-seguro")
DEBUG = os.getenv("DEBUG", "false").lower() == "true"

ALLOWED_HOSTS = [".vercel.app", "localhost", "127.0.0.1"]
_extra_hosts = os.getenv("ALLOWED_HOSTS", "").strip()
if _extra_hosts:
    ALLOWED_HOSTS.extend([h.strip() for h in _extra_hosts.split(",") if h.strip()])

CSRF_TRUSTED_ORIGINS = ["https://*.vercel.app"]
_extra_csrf = os.getenv("CSRF_TRUSTED_ORIGINS", "").strip()
if _extra_csrf:
    CSRF_TRUSTED_ORIGINS.extend([o.strip() for o in _extra_csrf.split(",") if o.strip()])

# ===========
# Apps/Middle
# ===========
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Apps propias
    "core",
]

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

ROOT_URLCONF = "api.urls"
WSGI_APPLICATION = "api.wsgi.application"


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

# =========================
#        BASE DE DATOS
# =========================

DATABASE_URL = os.getenv("DATABASE_URL", "").strip()

# Opción para forzar SQLite en local
USE_SQLITE = os.getenv("USE_SQLITE", "").lower() in {"1", "true", "yes"}

# Reconstruir DATABASE_URL a partir de piezas si fuese necesario
if not DATABASE_URL:
    u = os.getenv("DB_USER", "").strip()
    p = os.getenv("DB_PASSWORD", "").strip()
    h = os.getenv("DB_HOST", "").strip()
    pt = os.getenv("DB_PORT", "").strip()
    n = os.getenv("DB_NAME", "").strip()
    if all([u, p, h, pt, n]):
        DATABASE_URL = f"postgres://{u}:{p}@{h}:{pt}/{n}?sslmode=require"

IS_PROD = os.getenv("VERCEL", "") not in ("", "0", "false", "False") or not DEBUG

if IS_PROD and not USE_SQLITE:
    # Producción: exigir Postgres
    if not DATABASE_URL:
        raise RuntimeError(
            "DATABASE_URL no está definido. Configura la URL del pooler de Supabase."
        )
    import dj_database_url
    DATABASES = {
        "default": dj_database_url.config(
            default=DATABASE_URL, conn_max_age=600, ssl_require=True
        )
    }
else:
    # Desarrollo/local: si hay DATABASE_URL úsalo; si no, SQLite
    if DATABASE_URL:
        import dj_database_url
        DATABASES = {
            "default": dj_database_url.config(
                default=DATABASE_URL, conn_max_age=0, ssl_require=False
            )
        }
    else:
        DATABASES = {
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": BASE_DIR / "db.sqlite3",
            }
        }


# =================
# Password policies
# =================
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# =================
# Internacionalización
# =================
LANGUAGE_CODE = "es-es"
TIME_ZONE = os.getenv("TIME_ZONE", "Europe/Madrid")
USE_I18N = True
USE_TZ = True

# =================
# Estáticos / Media
# =================
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# =================
# Seguridad extra en prod
# =================
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_SSL_REDIRECT = os.getenv("SECURE_SSL_REDIRECT", "true").lower() == "true"
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

# =================
# Logging a consola (Vercel)
# =================
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "root": {"handlers": ["console"], "level": os.getenv("LOG_LEVEL", "INFO")},
}
