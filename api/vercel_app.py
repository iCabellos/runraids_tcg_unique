"""
Vercel-specific Django application setup.
This file handles the initialization for Vercel deployment.
"""
import os
import django
from django.core.wsgi import get_wsgi_application

# Set the settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'api.settings')

# Setup Django
django.setup()

# Run migrations and load data on first import (Vercel build)
if os.environ.get('VERCEL_ENV'):
    try:
        from django.core.management import execute_from_command_line
        from django.db import connection
        
        print("🔍 Vercel build: Checking database...")
        
        # Test database connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        
        print("✅ Database connection successful")
        
        # Apply migrations
        print("🔄 Applying migrations...")
        execute_from_command_line(['manage.py', 'migrate', '--noinput'])
        
        # Load initial data
        print("📦 Loading initial data...")
        execute_from_command_line(['manage.py', 'load_initial_data'])
        
        print("✅ Vercel build setup completed")
        
    except Exception as e:
        print(f"⚠️  Vercel build warning: {e}")
        # Don't fail the build, just log the warning

# Export the WSGI application
app = get_wsgi_application()
