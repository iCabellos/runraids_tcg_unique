#!/usr/bin/env python
"""
Script to diagnose common issues with the Django app.
"""
import os
import sys
import django
from pathlib import Path

# Setup Django
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'api.settings')

def check_static_files():
    """Check static files configuration."""
    print("📁 Checking static files configuration...")
    
    from django.conf import settings
    
    print(f"STATIC_URL: {settings.STATIC_URL}")
    print(f"STATIC_ROOT: {settings.STATIC_ROOT}")
    print(f"STATICFILES_DIRS: {settings.STATICFILES_DIRS}")
    
    # Check if static root exists
    if os.path.exists(settings.STATIC_ROOT):
        static_files = list(Path(settings.STATIC_ROOT).rglob('*'))
        print(f"✅ STATIC_ROOT exists with {len(static_files)} files")
    else:
        print("❌ STATIC_ROOT does not exist")
        print("💡 Run: python manage.py collectstatic")
    
    # Check admin static files specifically
    admin_static = Path(settings.STATIC_ROOT) / 'admin'
    if admin_static.exists():
        print("✅ Django admin static files found")
    else:
        print("❌ Django admin static files missing")

def check_database():
    """Check database connection and data."""
    print("\n🗄️  Checking database...")
    
    try:
        from django.db import connection
        from django.contrib.auth.models import User
        from core.models import Member
        
        # Test connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        print("✅ Database connection successful")
        
        # Check users
        admin_count = User.objects.filter(is_superuser=True).count()
        member_count = Member.objects.count()
        
        print(f"👤 Django admin users: {admin_count}")
        print(f"🎮 Game members: {member_count}")
        
        if admin_count == 0:
            print("⚠️  No admin users found")
        if member_count == 0:
            print("⚠️  No game members found")
            
    except Exception as e:
        print(f"❌ Database error: {e}")

def check_login_functionality():
    """Check login forms and functionality."""
    print("\n🔐 Checking login functionality...")
    
    try:
        from core.forms import MemberLoginForm
        from core.models import Member
        
        # Check if test members exist
        test_phones = [555000001, 123456789, 987654321, 111111111]
        for phone in test_phones:
            try:
                member = Member.objects.get(phone=phone)
                print(f"✅ Test member found: {member.name} ({phone})")
            except Member.DoesNotExist:
                print(f"❌ Test member not found: {phone}")
        
        print("💡 Try logging in with: 555000001 / test123")
        
    except Exception as e:
        print(f"❌ Login check error: {e}")

def main():
    print("🔍 RunRaids TCG - Diagnostic Tool")
    print("=" * 50)
    
    try:
        django.setup()
        
        check_static_files()
        check_database()
        check_login_functionality()
        
        print("\n🎯 Diagnostic completed!")
        print("\n💡 Common solutions:")
        print("   • Static files 404: python manage.py collectstatic")
        print("   • Login 500 error: python manage.py load_initial_data")
        print("   • Database issues: python manage.py migrate")
        
    except Exception as e:
        print(f"❌ Diagnostic error: {e}")
        return False
    
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
