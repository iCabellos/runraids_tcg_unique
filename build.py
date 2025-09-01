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

def main():
    try:
        print("Setting up Django...")
        django.setup()
        from django.core.management import execute_from_command_line

        print("Collecting static files...")
        execute_from_command_line(['manage.py', 'collectstatic', '--noinput', '--clear'])
        print("Static files collected successfully!")

        # Try to run migrations and load initial data
        try:
            print("Making migrations for 'core'...")
            execute_from_command_line(['manage.py', 'makemigrations', 'core', '--noinput'])
            print("Applying migrations...")
            execute_from_command_line(['manage.py', 'migrate', '--noinput'])
            print("Migrations applied.")
        except Exception as me:
            print(f"Warning: migration step failed: {me}")

        try:
            print("Loading initial data if available...")
            execute_from_command_line(['manage.py', 'load_initial_data'])
            print("Initial data loaded.")
        except Exception as le:
            print(f"Info: load_initial_data not executed: {le}")

        # Create a simple index file to indicate build success
        with open('build_success.txt', 'w') as f:
            f.write('Build completed successfully')

        return True

    except Exception as e:
        print(f"Warning: Could not collect static files: {e}")
        # Don't fail the build for static files
        return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
