"""
Django settings for runraids project.

Adaptado para Vercel + Supabase (Transaction Pooler).
En producción: Postgres obligatorio. En local: SQLite si no hay DATABASE_URL o si USE_SQLITE=true.
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# -----------------------------
# Carga de variables de entorno
# -----------------------------
def _make_env_reader():
    try:
        from decouple import Config, RepositoryEnv, AutoConfig  # type: ignore
        env_local = BASE_DIR / ".env.local"
        if env_local.exists():
            _cfg = Config(RepositoryEnv(str(env_local)))
            def _get(key, default=None):
                try:
                    return _cfg(key)
                except Exception:
                    return os.getenv(key, default)
        else:
            _auto = AutoConfig(search_path=str(BASE_DIR))
            def _get(key, default=None):
                try:
                    return _auto(key)
                except Exception:
                    return os.getenv(key, default)
        return _get
    except Exception:
        def _get(key, default=None):
            return os.getenv(key, default)
        return _get

ENV = _make_env_reader()

# -----------------
# Seguridad / Entorno
# -----------------
SECRET_KEY = ENV("SECRET_KEY", "dev-secret-key-no-seguro")
DEBUG = str(ENV("DEBUG", "false")).lower() == "true"
USE_SQLITE = str(ENV("USE_SQLITE", "false")).lower() in {"1", "true", "yes"}
DATABASE_URL = (ENV("DATABASE_URL", "") or "").strip()

ALLOWED_HOSTS = [".vercel.app", "localhost", "127.0.0.1"]
_extra_hosts = (ENV("ALLOWED_HOSTS", "") or "").strip()
if _extra_hosts:
    ALLOWED_HOSTS.extend([h.strip() for h in _extra_hosts.split(",") if h.strip()])

CSRF_TRUSTED_ORIGINS = ["https://*.vercel.app"]
_extra_csrf = (ENV("CSRF_TRUSTED_ORIGINS", "") or "").strip()
if _extra_csrf:
    CSRF_TRUSTED_ORIGINS.extend([o.strip() for o in _extra_csrf.split(",") if o.strip()])

# ----------
# Apps/Middleware
# ----------
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

# -------------
# Base de datos
# -------------
# Nota: 'producción' si estamos en Vercel o si DEBUG=False
IS_PROD = (str(ENV("VERCEL", "")).lower() in {"1", "true"}) or (not DEBUG)

if IS_PROD and not USE_SQLITE:
    # Producción: exigir Postgres
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL no está definido. Configura la URL del pooler de Supabase.")
    import dj_database_url  # type: ignore
    DATABASES = {
        "default": dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600,
            ssl_require=True,
        )
    }
else:
    # Desarrollo/local: usa DATABASE_URL si existe, si no SQLite
    if DATABASE_URL:
        import dj_database_url  # type: ignore
        DATABASES = {
            "default": dj_database_url.config(
                default=DATABASE_URL,
                conn_max_age=0,
                ssl_require=False,
            )
        }
    else:
        DATABASES = {
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": BASE_DIR / "db.sqlite3",
            }
        }

# --------------------
# Password policies
# --------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# --------------------
# Internacionalización
# --------------------
LANGUAGE_CODE = "es-es"
TIME_ZONE = ENV("TIME_ZONE", "Europe/Madrid")
USE_I18N = True
USE_TZ = True

# --------------------
# Estáticos / Media
# --------------------
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# --------------------
# Seguridad extra prod
# --------------------
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_SSL_REDIRECT = str(ENV("SECURE_SSL_REDIRECT", "true")).lower() == "true"
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

# --------------------
# Logging consola
# --------------------
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "root": {"handlers": ["console"], "level": ENV("LOG_LEVEL", "INFO")},
}
