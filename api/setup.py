"""
Setup script for RunRaids TCG - Vercel deployment.
This script handles database migrations and initial data loading.
"""
import os
import django
from django.core.management import execute_from_command_line

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'api.settings')
django.setup()

def setup_database():
    """Setup database with migrations and initial data."""
    try:
        print("🔄 Applying migrations...")
        execute_from_command_line(['manage.py', 'migrate', '--noinput'])
        print("✅ Migrations applied successfully")
        
        print("📦 Loading initial data...")
        execute_from_command_line(['manage.py', 'load_initial_data'])
        print("✅ Initial data loaded successfully")
        
        return True
    except Exception as e:
        print(f"❌ Setup error: {e}")
        return False

if __name__ == '__main__':
    setup_database()
