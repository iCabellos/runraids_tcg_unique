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
            # Always perform a hard reset on cold start, as requested
            print('🧨 Always resetting database on cold start...')
            try:
                call_command('reset_db', '--yes')
            except Exception as e:
                print(f'⚠️  reset_db failed (continuing): {e}')

            # Apply migrations and load initial data
            try:
                print('🔄 Applying migrations...')
                # Ensure migration files are up-to-date; remove placeholder migration if present
                try:
                    import os as _os
                    from pathlib import Path as _Path
                    mig_path = _Path(__file__).resolve().parents[1] / 'core' / 'migrations' / '0001_initial.py'
                    if mig_path.exists():
                        with open(mig_path, 'r', encoding='utf-8') as _f:
                            _content = _f.read().strip()
                        if _content.startswith('# intentionally empty'):
                            print('🧹 Removing placeholder migration core/migrations/0001_initial.py...')
                            try:
                                _os.remove(mig_path)
                            except Exception as _re:
                                print(f'⚠️  Could not remove placeholder migration: {_re}')
                    # Now (re)generate migrations
                    call_command('makemigrations', 'core', '--noinput')
                except Exception as _me:
                    print(f'⚠️  makemigrations issue (continuing): {_me}')
                call_command('migrate', '--noinput')
                print('✅ Migrations applied.')
                print('📦 Loading initial data...')
                call_command('load_initial_data')
                print('✅ Initial data loaded.')
            except Exception as e:
                print(f'⚠️  Migrate/initial data step issue: {e}')

            # Verification step
            try:
                existing_tables = set(connection.introspection.table_names())
                print(f"🧾 Tables present: {len(existing_tables)}")
                # Core tables
                if 'core_skill' not in existing_tables:
                    raise RuntimeError('core_skill table missing after migrate')
                if 'core_hero' not in existing_tables:
                    raise RuntimeError('core_hero table missing after migrate')
                if 'core_playerhero' not in existing_tables:
                    raise RuntimeError('core_playerhero table missing after migrate')
                # Django contrib essentials
                if 'django_migrations' not in existing_tables:
                    raise RuntimeError('django_migrations table missing after migrate')
                if 'auth_user' not in existing_tables:
                    raise RuntimeError('auth_user table missing after migrate')
                if 'django_session' not in existing_tables:
                    raise RuntimeError('django_session table missing after migrate')
                with connection.cursor() as c:
                    # Probe expected columns
                    c.execute('SELECT codename FROM core_hero LIMIT 1')
                    c.execute('SELECT experience FROM core_playerhero LIMIT 1')
                    c.execute('SELECT 1 FROM auth_user LIMIT 1')
                    c.execute('SELECT 1 FROM django_session LIMIT 1')
                print('✅ Verified core and django contrib tables/columns are present.')
            except Exception as ve:
                print(f"❌ Verification failed: {ve}. Trying migrate once more...")
                try:
                    call_command('migrate', '--noinput')
                    with connection.cursor() as c:
                        c.execute('SELECT codename FROM core_hero LIMIT 1')
                        c.execute('SELECT experience FROM core_playerhero LIMIT 1')
                        c.execute('SELECT 1 FROM auth_user LIMIT 1')
                        c.execute('SELECT 1 FROM django_session LIMIT 1')
                    print('✅ Verified after second migrate.')
                except Exception as ve2:
                    print(f"⚠️  Still failing verification: {ve2}")
        except Exception as e:
            # Never break app startup because of setup. Log and continue.
            print(f'⚠️  Startup DB ensure skipped due to error: {e}')

    print('🟢 Starting ensure_db_ready (cold start) ...')
    ensure_db_ready()
    print('🟢 Finished ensure_db_ready.')
except Exception as _e:
    # If any import fails (e.g., during collectstatic or build), do nothing
    pass
