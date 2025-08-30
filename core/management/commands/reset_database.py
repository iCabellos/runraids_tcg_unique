"""
Django management command to reset the database completely.
This will delete all data and reload initial data.
"""
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.contrib.auth.models import User

try:
    from core.models import (
        ResourceType, BuildingType, Rarity, Ability, Hero, Enemy, Member,
        PlayerResource, PlayerHero, BuildingLevelCost, PlayerBuilding
    )
    models_available = True
except ImportError as e:
    models_available = False
    import_error = str(e)


class Command(BaseCommand):
    help = 'Reset database completely and reload initial data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Confirm that you want to delete all data',
        )

    def handle(self, *args, **options):
        if not models_available:
            self.stdout.write(
                self.style.ERROR(f'Models not available: {import_error}')
            )
            return

        if not options['confirm']:
            self.stdout.write(
                self.style.WARNING('⚠️  This will DELETE ALL DATA in the database!')
            )
            self.stdout.write('To confirm, run: python manage.py reset_database --confirm')
            return

        self.stdout.write('🗑️  Resetting database...')

        try:
            # Delete all data in correct order to avoid foreign key constraints
            self.stdout.write('Deleting game data...')
            PlayerHero.objects.all().delete()
            PlayerResource.objects.all().delete()
            PlayerBuilding.objects.all().delete()
            BuildingLevelCost.objects.all().delete()
            Member.objects.all().delete()
            Hero.objects.all().delete()
            Enemy.objects.all().delete()
            Ability.objects.all().delete()
            Rarity.objects.all().delete()
            BuildingType.objects.all().delete()
            ResourceType.objects.all().delete()

            # Delete admin users (except manually created superusers)
            self.stdout.write('Deleting admin users...')
            User.objects.filter(username__in=['admin']).delete()

            self.stdout.write(
                self.style.SUCCESS('✅ All data deleted successfully')
            )

            # Reload initial data
            self.stdout.write('📦 Reloading initial data...')
            call_command('load_initial_data')

            self.stdout.write(
                self.style.SUCCESS('🎉 Database reset completed successfully!')
            )
            self.stdout.write('\n🎮 Available users:')
            self.stdout.write('   • Django Admin: admin/admin')
            self.stdout.write('   • Test Member: 555000001/test123')
            self.stdout.write('   • Test Player 1: 123456789/testpass123')
            self.stdout.write('   • Test Player 2: 987654321/testpass123')

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error resetting database: {e}')
            )
