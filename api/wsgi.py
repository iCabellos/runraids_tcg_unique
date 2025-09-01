"""
WSGI config for runraids project.

It exposes the WSGI callable as a module-level variable named ``app``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'api.settings')

app = get_wsgi_application()

# One-time safety net: if core auth tables are missing (fresh DB),
# apply migrations and load initial data. This is idempotent and will not
# overwrite existing records because our load_initial_data uses get_or_create
# and defaults, and migrate is safe to re-run.
try:
    from django.db import connection
    from django.core.management import call_command

    def ensure_db_ready():
        try:
            # One-off hard reset if requested via env
            if os.environ.get('RESET_DB') == '1':
                print('🧨 RESET_DB=1 detected → resetting database...')
                try:
                    call_command('reset_db', '--yes')
                except Exception as e:
                    print(f'⚠️  reset_db failed: {e}')
                return

            existing_tables = set(connection.introspection.table_names())
            needs_migrate = False
            if 'django_migrations' not in existing_tables:
                needs_migrate = True
            else:
                # If key core tables missing or model columns missing, force migrate
                if 'core_skill' not in existing_tables or 'core_hero' not in existing_tables:
                    needs_migrate = True
                else:
                    try:
                        with connection.cursor() as c:
                            # Probe for columns that should exist; ignore errors
                            c.execute('SELECT 1 FROM core_hero LIMIT 1')
                    except Exception:
                        needs_migrate = True
            # Allow forcing a full reset via env on next deploy
            if os.environ.get('FORCE_MIGRATIONS') == '1':
                print('🧰 FORCE_MIGRATIONS=1 → applying migrations now...')
                needs_migrate = True
            if needs_migrate:
                print('🔄 Ensuring migrations are applied...')
                # Try a lightweight makemigrations (no-op if up-to-date)
                try:
                    call_command('makemigrations', 'core', '--noinput')
                except Exception:
                    pass
                call_command('migrate', '--noinput')
                print('✅ Migrations completed.')
                # Load initial data only after migrations, non-destructive
                try:
                    print('📦 Loading initial data (idempotent)...')
                    call_command('load_initial_data')
                    print('✅ Initial data ensured.')
                except Exception as e:
                    print(f'⚠️  Initial data load skipped: {e}')
            else:
                # Optional: we can still ensure initial data existence without modifying existing
                # but to avoid overhead on every cold start, we skip if tables exist.
                pass
        except Exception as e:
            # Never break app startup because of setup. Log and continue.
            print(f'⚠️  Startup DB ensure skipped due to error: {e}')

    ensure_db_ready()
except Exception as _e:
    # If any import fails (e.g., during collectstatic or build), do nothing
    pass
