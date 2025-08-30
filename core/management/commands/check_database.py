"""
Django management command to check database connection and data.
"""
from django.core.management.base import BaseCommand
from django.db import connection
from django.contrib.auth.models import User

try:
    from core.models import Member, ResourceType, Hero, BuildingType
    models_available = True
except ImportError:
    models_available = False


class Command(BaseCommand):
    help = 'Check database connection and verify data'

    def handle(self, *args, **options):
        self.stdout.write('🔍 Checking database connection and data...')
        
        # Check database connection
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                if result:
                    self.stdout.write(
                        self.style.SUCCESS('✅ Database connection: OK')
                    )
                else:
                    self.stdout.write(
                        self.style.ERROR('❌ Database connection: FAILED')
                    )
                    return
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Database connection error: {e}')
            )
            return

        # Check database type
        db_vendor = connection.vendor
        db_name = connection.settings_dict.get('NAME', 'Unknown')
        self.stdout.write(f'📊 Database type: {db_vendor}')
        if db_vendor == 'postgresql':
            host = connection.settings_dict.get('HOST', 'Unknown')
            self.stdout.write(f'🌐 Database host: {host}')
        elif db_vendor == 'sqlite':
            self.stdout.write(f'📁 Database file: {db_name}')

        # Check Django admin users
        try:
            admin_users = User.objects.filter(is_superuser=True)
            self.stdout.write(f'👤 Django admin users: {admin_users.count()}')
            for user in admin_users:
                self.stdout.write(f'   - {user.username} ({user.email})')
        except Exception as e:
            self.stdout.write(
                self.style.WARNING(f'⚠️  Could not check admin users: {e}')
            )

        if not models_available:
            self.stdout.write(
                self.style.WARNING('⚠️  Core models not available, skipping game data check')
            )
            return

        # Check core models data
        try:
            # Check Members
            members_count = Member.objects.count()
            self.stdout.write(f'🎮 Game members: {members_count}')
            
            # Check Resource Types
            resources_count = ResourceType.objects.count()
            self.stdout.write(f'💰 Resource types: {resources_count}')
            
            # Check Heroes
            heroes_count = Hero.objects.count()
            self.stdout.write(f'🦸 Heroes: {heroes_count}')
            
            # Check Building Types
            buildings_count = BuildingType.objects.count()
            self.stdout.write(f'🏗️  Building types: {buildings_count}')
            
            if all([members_count > 0, resources_count > 0, heroes_count > 0, buildings_count > 0]):
                self.stdout.write(
                    self.style.SUCCESS('✅ All game data loaded successfully!')
                )
            else:
                self.stdout.write(
                    self.style.WARNING('⚠️  Some game data is missing. Run: python manage.py load_initial_data')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error checking game data: {e}')
            )

        self.stdout.write('\n🎯 Database check completed!')
