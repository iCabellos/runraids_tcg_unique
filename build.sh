#!/bin/bash

echo "🚀 Starting Vercel build for RunRaids TCG..."

# Install dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Set Django settings module
export DJANGO_SETTINGS_MODULE=api.settings

# Check if we have database connection
echo "🔍 Checking database connection..."
python -c "
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'api.settings')
django.setup()
from django.db import connection
try:
    with connection.cursor() as cursor:
        cursor.execute('SELECT 1')
    print('✅ Database connection successful')
except Exception as e:
    print(f'❌ Database connection failed: {e}')
    exit(1)
"

# Apply migrations
echo "🔄 Applying database migrations..."
python manage.py migrate --noinput

# Load initial data
echo "📦 Loading initial data..."
python manage.py load_initial_data

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

echo "✅ Build completed successfully!"
