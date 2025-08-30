#!/usr/bin/env python
"""
Build script for Vercel deployment.
Collects static files for Django admin.
"""
import os
import sys
import django
from pathlib import Path

# Setup Django
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'api.settings')

try:
    django.setup()
    from django.core.management import execute_from_command_line
    
    print("Collecting static files...")
    execute_from_command_line(['manage.py', 'collectstatic', '--noinput'])
    print("Static files collected successfully!")
    
except Exception as e:
    print(f"Warning: Could not collect static files: {e}")
    # Don't fail the build for static files
    pass
