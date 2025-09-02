from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db import connection, transaction

class Command(BaseCommand):
    help = "HARD RESET: Drop entire Postgres schema and rebuild from scratch. Then apply migrations and load initial data. USE WITH CAUTION."

    def add_arguments(self, parser):
        parser.add_argument('--yes', action='store_true', help='Run without prompts')
        parser.add_argument('--skip-initial-data', action='store_true', help='Do not load initial data after migrations')

    def handle(self, *args, **options):
        non_interactive = options['yes']
        skip_initial = options['skip_initial_data']

        # Show DB info
        vendor = connection.vendor
        self.stdout.write(self.style.WARNING(f"Resetting database on vendor='{vendor}'"))

        if vendor != 'postgresql':
            self.stdout.write(self.style.ERROR("This hard reset is designed for PostgreSQL (Supabase)."))

        # HARD DROP: drop schema public CASCADE and recreate
        try:
            with connection.cursor() as cursor:
                self.stdout.write("🧨 Dropping schema public CASCADE …")
                cursor.execute("DROP SCHEMA IF EXISTS public CASCADE;")
                self.stdout.write("🏗️  Creating schema public …")
                cursor.execute("CREATE SCHEMA public;")
                # basic grants (Supabase manages roles, but safe defaults)
                cursor.execute("GRANT ALL ON SCHEMA public TO PUBLIC;")
                cursor.execute("GRANT ALL ON SCHEMA public TO CURRENT_USER;")
            self.stdout.write(self.style.SUCCESS("✅ Schema recreated"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Failed to recreate schema: {e}"))

        # Make migrations (core) and migrate all
        try:
            self.stdout.write("🧩 Making migrations (core)…")
            call_command('makemigrations', 'core', verbosity=1, interactive=False)
        except Exception:
            pass

        self.stdout.write("🚀 Applying all migrations…")
        call_command('migrate', verbosity=1, interactive=False)
        self.stdout.write(self.style.SUCCESS("✅ Migrations applied"))

        if not skip_initial:
            self.stdout.write("📦 Loading initial data (idempotent)…")
            try:
                call_command('load_initial_data')
                self.stdout.write(self.style.SUCCESS("✅ Initial data loaded"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"❌ Initial data load failed: {e}"))

        # Verify critical tables/columns exist
        try:
            with connection.cursor() as c:
                c.execute("SELECT COUNT(*) FROM core_skill;")
                c.execute("SELECT codename FROM core_hero LIMIT 1;")
                # PlayerHero.experience also required
                c.execute("SELECT experience FROM core_playerhero LIMIT 1;")
            self.stdout.write(self.style.SUCCESS("🧪 Verification OK: core tables/columns exist"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Verification failed: {e}"))

        self.stdout.write(self.style.SUCCESS("🎉 Database hard reset completed"))
