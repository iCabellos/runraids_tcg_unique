#!/usr/bin/env python
"""
Script to create and apply migrations for the model fixes.
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
    
    print("🔄 Creating migrations for model fixes...")
    execute_from_command_line(['manage.py', 'makemigrations', 'core'])
    
    print("🔄 Applying migrations...")
    execute_from_command_line(['manage.py', 'migrate'])
    
    print("✅ Migrations completed successfully!")
    
except Exception as e:
    print(f"❌ Error with migrations: {e}")
    sys.exit(1)
