from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db import connection

class Command(BaseCommand):
    help = "Reset the database schema to a clean state and re-apply all migrations, then load initial data. Intended for one-off use during major schema changes."

    def add_arguments(self, parser):
        parser.add_argument('--yes', action='store_true', help='Run without prompts')
        parser.add_argument('--skip-initial-data', action='store_true', help='Do not load initial data after migrations')

    def handle(self, *args, **options):
        non_interactive = options['yes']
        skip_initial = options['skip_initial_data']

        apps_to_reset = ['core', 'admin', 'auth', 'sessions', 'contenttypes']

        # Show DB info
        vendor = connection.vendor
        self.stdout.write(self.style.WARNING(f"Resetting database on vendor='{vendor}'"))

        # Unapply migrations for target apps
        for app in apps_to_reset:
            try:
                self.stdout.write(f"🔄 Unapplying migrations for {app} → zero ...")
                call_command('migrate', app, 'zero', verbosity=1, interactive=not non_interactive)
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"⚠️  Could not unapply {app}: {e}"))

        # Re-apply migrations
        try:
            self.stdout.write("🧩 Making migrations (just in case)...")
            call_command('makemigrations', 'core', verbosity=1, interactive=False)
        except Exception:
            # Ignore if no changes
            pass

        self.stdout.write("🚀 Applying all migrations...")
        call_command('migrate', verbosity=1, interactive=False)
        self.stdout.write(self.style.SUCCESS("✅ Migrations applied"))

        if not skip_initial:
            self.stdout.write("📦 Loading initial data (will insert only missing records)...")
            try:
                call_command('load_initial_data')
                self.stdout.write(self.style.SUCCESS("✅ Initial data loaded"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"❌ Initial data load failed: {e}"))

        self.stdout.write(self.style.SUCCESS("🎉 Database reset completed"))
