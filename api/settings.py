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

# Load environment variables from .env file
# Check if we're in production (Vercel) or development
print(f"🔍 VERCEL_ENV: {os.environ.get('VERCEL_ENV')}")
print(f"🔍 VERCEL: {os.environ.get('VERCEL')}")
print(f"🔍 BASE_DIR: {BASE_DIR}")

if os.environ.get('VERCEL_ENV') or os.environ.get('VERCEL'):
    # Production - load .env.production
    env_file = BASE_DIR / '.env.production'
    print(f"🔍 Looking for: {env_file}")
    print(f"🔍 File exists: {env_file.exists()}")

    if env_file.exists():
        load_dotenv(env_file)
        print("🚀 Loaded .env.production for Vercel")
        # Print file contents for debug
        with open(env_file, 'r') as f:
            content = f.read()
            print(f"🔍 .env.production content: {content[:100]}...")
    else:
        print("⚠️  .env.production not found, using default .env")
        load_dotenv()
else:
    # Development - load .env
    load_dotenv()
    print("🔧 Loaded .env for local development")

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-&9$1wr5oe9m(a6*=u_85*!mlpf%j&2(0ow6wd^4v#+ohy-*q8j')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', 'True').lower() == 'true'

# Vercel deployment hosts (following official template)
ALLOWED_HOSTS = ['127.0.0.1', '.vercel.app']

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
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'api.wsgi.app'

# Database configuration using Supabase
# Use DATABASE_URL directly as it's more reliable
database_url = os.getenv('DATABASE_URL')

if database_url:
    import dj_database_url
    DATABASES = {
        'default': dj_database_url.parse(database_url)
    }
    # Add SSL requirement for Supabase
    DATABASES['default']['OPTIONS'] = {
        'sslmode': 'require',
    }
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

# Whitenoise configuration for serving static files

# Whitenoise settings - Use simple storage to avoid manifest issues
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
