"""
WSGI config for runraids project.

It exposes the WSGI callable as a module-level variable named ``app``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'api.settings')

# One-time safety net: if core auth tables are missing (fresh DB),
# try to apply migrations and load initial data. Avoid destructive operations.
try:
    from django.db import connection
    from django.core.management import call_command

    def ensure_db_ready():
        try:
            # Check if auth_user table exists; if not, run migrations
            existing_tables = set()
            try:
                existing_tables = set(connection.introspection.table_names())
                print(f"🧾 Tables at startup: {len(existing_tables)}")
            except Exception as tb_e:
                print(f"⚠️  Could not list tables at startup: {tb_e}")

            if 'auth_user' not in existing_tables or 'django_migrations' not in existing_tables:
                print('🔄 Applying migrations (startup)...')
                try:
                    call_command('migrate', '--noinput')
                    print('✅ Migrations applied.')
                except Exception as e:
                    print(f'⚠️  migrate failed (continuing): {e}')

            # Try to load initial data if core tables are present but data likely missing
            try:
                if 'core_hero' in existing_tables:
                    print('📦 Loading initial data (startup)...')
                    call_command('load_initial_data')
                    print('✅ Initial data loaded.')
            except Exception as e:
                print(f'⚠️  Initial data load skipped/failed: {e}')
        except Exception as e:
            # Never break app startup because of setup. Log and continue.
            print(f'⚠️  Startup DB ensure skipped due to error: {e}')

    print('🟢 Starting ensure_db_ready (cold start) ...')
    ensure_db_ready()
    print('🟢 Finished ensure_db_ready.')
except Exception as _e:
    # If any import fails (e.g., during collectstatic or build), do nothing
    pass

# Now create the WSGI application after DB is ready
app = get_wsgi_application()
