#!/usr/bin/env python
"""
Script to setup the database for RunRaids TCG.
This script will:
1. Check database connection
2. Apply migrations
3. Load initial data
4. Verify everything is working
"""
import os
import sys
import django
from pathlib import Path

# Add the project directory to Python path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'api.settings')
django.setup()

from django.core.management import execute_from_command_line
from django.db import connection
from django.contrib.auth.models import User


def print_header(text):
    print(f"\n{'='*50}")
    print(f"🎮 {text}")
    print(f"{'='*50}")


def print_step(step, text):
    print(f"\n{step}. {text}")


def check_database_connection():
    """Check if database connection is working."""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            if result:
                print("✅ Database connection: OK")
                db_vendor = connection.vendor
                print(f"📊 Database type: {db_vendor}")
                return True
            else:
                print("❌ Database connection: FAILED")
                return False
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        return False


def run_migrations():
    """Apply database migrations."""
    print("🔄 Applying migrations...")
    try:
        execute_from_command_line(['manage.py', 'migrate'])
        print("✅ Migrations applied successfully")
        return True
    except Exception as e:
        print(f"❌ Error applying migrations: {e}")
        return False


def load_initial_data(force_reload=False):
    """Load initial data from JSON file."""
    print("📦 Loading initial data...")
    try:
        if force_reload:
            execute_from_command_line(['manage.py', 'load_initial_data', '--clear'])
        else:
            execute_from_command_line(['manage.py', 'load_initial_data'])
        print("✅ Initial data loaded successfully")
        return True
    except Exception as e:
        print(f"❌ Error loading initial data: {e}")
        print("💡 Try running with --clear option to reset existing data")
        return False


def verify_setup():
    """Verify that everything is set up correctly."""
    print("🔍 Verifying setup...")
    try:
        execute_from_command_line(['manage.py', 'check_database'])
        return True
    except Exception as e:
        print(f"❌ Error during verification: {e}")
        return False


def main():
    print_header("RunRaids TCG Database Setup")
    
    # Check if .env file exists
    env_file = BASE_DIR / '.env'
    if not env_file.exists():
        print("⚠️  Warning: .env file not found!")
        print("📝 Please create a .env file based on .env.example")
        print("🔗 See DATABASE_SETUP_GUIDE.md for detailed instructions")
        
        response = input("\nDo you want to continue anyway? (y/N): ")
        if response.lower() != 'y':
            print("❌ Setup cancelled. Please create .env file first.")
            return False
    
    print_step(1, "Checking database connection")
    if not check_database_connection():
        print("\n❌ Database connection failed!")
        print("🔧 Please check your DATABASE_URL in .env file")
        print("📖 See DATABASE_SETUP_GUIDE.md for help")
        return False
    
    print_step(2, "Applying database migrations")
    if not run_migrations():
        print("\n❌ Migration failed!")
        return False
    
    print_step(3, "Loading initial data")
    # Check if data already exists
    try:
        from django.contrib.auth.models import User
        from core.models import Member

        existing_users = User.objects.count()
        existing_members = Member.objects.count()

        if existing_users > 0 or existing_members > 0:
            print(f"⚠️  Found existing data: {existing_users} Django users, {existing_members} game members")
            response = input("Do you want to clear existing data and reload? (y/N): ")
            if response.lower() == 'y':
                if not load_initial_data(force_reload=True):
                    print("\n❌ Initial data loading failed!")
                    return False
            else:
                print("📦 Skipping data loading (existing data preserved)")
        else:
            if not load_initial_data():
                print("\n❌ Initial data loading failed!")
                return False
    except Exception as e:
        print(f"⚠️  Could not check existing data: {e}")
        if not load_initial_data():
            print("\n❌ Initial data loading failed!")
            return False
    
    print_step(4, "Verifying setup")
    if not verify_setup():
        print("\n❌ Verification failed!")
        return False
    
    print_header("Setup Complete! 🎉")
    print("✅ Database setup completed successfully!")
    print("\n🎮 You can now:")
    print("   • Run the server: python manage.py runserver")
    print("   • Access admin panel: http://localhost:8000/admin/ (admin/admin)")
    print("   • Play the game: http://localhost:8000/")
    print("\n📚 Available users:")
    print("   • Django Admin: admin/admin")
    print("   • Test Member: 555000001/test123")
    print("   • Test Player 1: 123456789/testpass123")
    print("   • Test Player 2: 987654321/testpass123")
    
    return True


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
