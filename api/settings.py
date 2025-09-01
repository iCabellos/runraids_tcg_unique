"""
Django settings for runraids project - Vercel deployment.

Based on Vercel's official Django template with Supabase integration.
Uses .env files for all configuration.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables
# For local development, load from .env file
# For production (Vercel), use environment variables directly
if os.environ.get('VERCEL_ENV') or os.environ.get('VERCEL'):
    # Production - prefer environment variables, but load .env.production if present
    print("🚀 Running on Vercel - using environment variables")
    env_prod_path = BASE_DIR / '.env.production'
    if env_prod_path.exists():
        load_dotenv(dotenv_path=env_prod_path)
        print("📦 Loaded .env.production")
else:
    # Development - load .env
    load_dotenv()
    print("🔧 Local development - loaded .env file")

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-&9$1wr5oe9m(a6*=u_85*!mlpf%j&2(0ow6wd^4v#+ohy-*q8j')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', 'True').lower() == 'true'

# Vercel deployment hosts (following official template)
ALLOWED_HOSTS = ['127.0.0.1', 'localhost', '.vercel.app']
# CSRF trusted origins for POST requests from Vercel domains
CSRF_TRUSTED_ORIGINS = ['https://*.vercel.app']

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Own apps
    'core',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Add whitenoise for static files
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'api.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'core' / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.static',
            ],
        },
    },
]

WSGI_APPLICATION = 'api.wsgi.app'

# Database configuration using Supabase
# Prefer DATABASE_URL; fallback to individual parameters if needed
import dj_database_url

# Read potential inputs (support both lowercase and DB_* variants)
raw_database_url = os.getenv('DATABASE_URL')
USER = os.getenv('user') or os.getenv('DB_USER')
PASSWORD = os.getenv('password') or os.getenv('DB_PASSWORD')
HOST = os.getenv('host') or os.getenv('DB_HOST')
PORT = os.getenv('port') or os.getenv('DB_PORT')
DBNAME = os.getenv('dbname') or os.getenv('DB_NAME')
FORCE_POOLER = (os.getenv('FORCE_POOLER', '0').lower() in {'1', 'true', 'yes'})

# Decide effective database_url
database_url = None if FORCE_POOLER else raw_database_url

# If no DATABASE_URL (or FORCE_POOLER), construct from individual env vars
if all([(USER or '').strip(), (PASSWORD or '').strip(), (HOST or '').strip(), (PORT or '').strip(), (DBNAME or '').strip()]):
    if not database_url:
        database_url = f"postgresql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DBNAME}"
        reason = "FORCE_POOLER" if FORCE_POOLER else "individual env vars"
        print(f"ℹ️ Constructed DATABASE_URL from {reason}")

# Defensive override logic: ensure pooler credentials are used
try:
    def _looks_like_plain_instance(url: str) -> bool:
        if not url:
            return False
        lowered = url.lower()
        # Any direct instance or default supabase port 5432
        return ('@db.' in lowered and ':5432/' in lowered) or 'supabase.co:5432' in lowered

    def _username_is_plain_postgres(url: str) -> bool:
        try:
            cfg = dj_database_url.parse(url)
            return (cfg.get('USER') or '').strip() == 'postgres'
        except Exception:
            return False

    def _host_is_pooler(url: str) -> bool:
        try:
            cfg = dj_database_url.parse(url)
            return 'pooler.supabase.com' in (cfg.get('HOST') or '')
        except Exception:
            return False

    pooler_vars_present = all([
        (USER or '').strip(), (PASSWORD or '').strip(), (HOST or '').strip(), (PORT or '').strip(), (DBNAME or '').strip()
    ]) and ('pooler.supabase.com' in (HOST or ''))

    if database_url and pooler_vars_present:
        # Override if URL looks like direct instance or username is plain 'postgres'
        if _looks_like_plain_instance(database_url) or _username_is_plain_postgres(database_url):
            database_url = f"postgresql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DBNAME}"
            print("🔁 Overriding DATABASE_URL → using Supabase Pooler based on individual vars (reason: plain instance or username 'postgres')")
        # Also override if URL host is pooler but username is still 'postgres'
        elif _host_is_pooler(database_url) and _username_is_plain_postgres(database_url):
            database_url = f"postgresql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DBNAME}"
            print("🔁 Overriding DATABASE_URL → pooler detected but username was 'postgres'")
except Exception as _e:
    # Do not fail settings due to diagnostics
    pass

if database_url:
    DATABASES = {
        'default': dj_database_url.parse(database_url, conn_max_age=60)
    }
    # Add SSL requirement and timeouts for Supabase
    options = DATABASES['default'].setdefault('OPTIONS', {})
    options.update({
        'sslmode': 'require',
        'connect_timeout': 10,
    })
    # Safe diagnostics (mask password)
    try:
        cfg = dj_database_url.parse(database_url)
        effective_user = (cfg.get('USER') or '')
        effective_host = (cfg.get('HOST') or '')
        effective_port = (cfg.get('PORT') or '')
        masked_user = (effective_user[:6] + '...') if effective_user else ''
        print(f"🗄️  Using DB → user={masked_user} host={effective_host} port={effective_port}")
    except Exception:
        print(f"🗄️  Using DATABASE_URL: {database_url[:80]}...")
else:
    # Final fallback - empty databases for serverless
    DATABASES = {}
    print("⚠️  No DATABASE_URL found")

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'es-es'
TIME_ZONE = 'Europe/Madrid'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
# Optionally include a project-level static directory
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'core', 'static'),
]

# Media files (uploads from ImageField/FileField)
MEDIA_URL = '/media/'
# In Vercel serverless runtime, the filesystem is read-only; use /tmp for uploads
if os.environ.get('VERCEL_ENV') or os.environ.get('VERCEL'):
    MEDIA_ROOT = '/tmp/media'
else:
    MEDIA_ROOT = os.path.join(BASE_DIR, 'core', 'media')

# Whitenoise configuration for serving static files
# On Vercel, serve directly from finders to avoid relying on collectstatic outputs from a separate build step
if os.environ.get('VERCEL_ENV') or os.environ.get('VERCEL'):
    # Use non-manifest storage and enable finders so core/static and admin assets are served at runtime
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'
    WHITENOISE_USE_FINDERS = True
else:
    # Locally we can use the manifest storage
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
