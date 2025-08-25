"""
Django settings for runraids project.

Generado con Django 5.1.6 y adaptado para despliegue en Vercel + Supabase.
"""

import os
from pathlib import Path
import dj_database_url

# --- Paths base ---
BASE_DIR = Path(__file__).resolve().parent.parent

# --- Seguridad / entorno ---
# Proporciona SECRET_KEY vía env en Vercel. En local, usa .env o export.
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-no-seguro")

# DEBUG desde env (por defecto False en despliegue)
DEBUG = os.getenv("DEBUG", "false").lower() == "true"

# Hosts permitidos (incluye dominios de Vercel)
ALLOWED_HOSTS = list(
    filter(
        None,
        [
            ".vercel.app",
            "localhost",
            "127.0.0.1",
            # Permite definir hosts extra por env, separados por comas
            *[h.strip() for h in os.getenv("ALLOWED_HOSTS", "").split(",")] if os.getenv("ALLOWED_HOSTS") else None,
        ],
    )
)

# Orígenes de confianza para CSRF (Vercel y dominio custom opcional)
CSRF_TRUSTED_ORIGINS = [
    "https://*.vercel.app",
]
_custom_origin = os.getenv("CSRF_TRUSTED_ORIGIN")
if _custom_origin:
    CSRF_TRUSTED_ORIGINS.append(_custom_origin)

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
# En Vercel/Supabase usa DATABASE_URL (Transaction Pooler con sslmode=require).
# En local, si no hay DATABASE_URL, cae a SQLite por comodidad.
_database_url = os.getenv("DATABASE_URL", "").strip()
if _database_url:
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
    # Vercel está detrás de proxy/edge -> respeta cabecera para HTTPS
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
