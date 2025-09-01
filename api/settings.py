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

database_url = os.getenv('DATABASE_URL')

if not database_url:
    # Construct from individual env vars if provided
    USER = os.getenv('user')
    PASSWORD = os.getenv('password')
    HOST = os.getenv('host')
    PORT = os.getenv('port')
    DBNAME = os.getenv('dbname')
    if all([USER, PASSWORD, HOST, PORT, DBNAME]):
        database_url = f"postgresql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DBNAME}"
        print("ℹ️ Constructed DATABASE_URL from individual env vars")

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
