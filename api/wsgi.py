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
            if 'auth_user' not in existing_tables or 'django_migrations' not in existing_tables:
                print('🔄 No core tables found. Running migrations...')
                call_command('migrate', '--noinput')
                print('✅ Migrations completed.')
                # Load initial data only after migrations, non-destructive
                print('📦 Loading initial data (idempotent)...')
                call_command('load_initial_data')
                print('✅ Initial data ensured.')
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
