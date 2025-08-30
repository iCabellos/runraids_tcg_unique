#!/usr/bin/env python
"""
Script to collect static files for deployment.
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
    
    print("📁 Collecting static files...")
    execute_from_command_line(['manage.py', 'collectstatic', '--noinput', '--clear'])
    print("✅ Static files collected successfully!")
    
except Exception as e:
    print(f"❌ Error collecting static files: {e}")
    sys.exit(1)
