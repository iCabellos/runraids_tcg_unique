#!/usr/bin/env python
"""
Simple script to check database setup.
"""
import os
import sys
import django
from pathlib import Path

# Setup Django
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'api.settings')


def check_db_setup():
    try:
        django.setup()
        from django.db import connection
        from django.contrib.auth.models import User
        
        print("🔍 Checking database configuration...")
        
        # Check .env file
        env_file = BASE_DIR / '.env'
        if env_file.exists():
            print("✅ .env file found")
            with open(env_file, 'r') as f:
                content = f.read()
                if 'DATABASE_URL' in content:
                    print("✅ DATABASE_URL configured in .env")
                else:
                    print("❌ DATABASE_URL not found in .env")
        else:
            print("❌ .env file not found")
        
        # Check database connection
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            print("✅ Database connection successful")
            
            # Check database type
            db_vendor = connection.vendor
            if db_vendor == 'postgresql':
                print("✅ Using PostgreSQL (Supabase)")
                host = connection.settings_dict.get('HOST', 'Unknown')
                if 'supabase' in host or 'pooler.supabase.com' in host:
                    print("✅ Connected to Supabase")
                else:
                    print(f"ℹ️  Connected to: {host}")
            elif db_vendor == 'sqlite':
                print("⚠️  Using SQLite (not Supabase)")
                print("💡 Configure DATABASE_URL in .env to use Supabase")
            
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            return False
        
        # Check if tables exist
        try:
            User.objects.count()
            print("✅ Django tables exist")
        except Exception as e:
            print(f"❌ Django tables missing: {e}")
            print("💡 Run: python manage.py migrate")
            return False
        
        # Check if data is loaded
        try:
            from core.models import Member
            admin_users = User.objects.filter(is_superuser=True).count()
            members = Member.objects.count()
            
            print(f"ℹ️  Django admin users: {admin_users}")
            print(f"ℹ️  Game members: {members}")
            
            if admin_users == 0:
                print("💡 No admin users found. Run: python manage.py load_initial_data")
            if members == 0:
                print("💡 No game members found. Run: python manage.py load_initial_data")
                
        except Exception as e:
            print(f"⚠️  Could not check game data: {e}")
        
        print("\n🎯 Database check completed!")
        return True
        
    except Exception as e:
        print(f"❌ Setup error: {e}")
        return False


if __name__ == '__main__':
    success = check_db_setup()
    if success:
        print("\n✅ Everything looks good!")
        print("🎮 You can run: python manage.py runserver")
    else:
        print("\n❌ Please fix the issues above")
    sys.exit(0 if success else 1)
