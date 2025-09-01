#!/usr/bin/env python
"""
Hard reset Supabase Postgres schema and re-create from scratch using Django migrations.
Use with caution. Requires env configured to Supabase pooler.
"""
import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'api.settings')

from django.core.management import execute_from_command_line


def main():
    # Ensure non-interactive
    args = ['manage.py', 'reset_db', '--yes']
    print('🧨 Running hard reset of the database (reset_db --yes) ...')
    try:
        execute_from_command_line(args)
    except SystemExit as e:
        # management commands may call sys.exit
        code = e.code or 0
        if code != 0:
            raise
    print('✅ Hard reset completed.')


if __name__ == '__main__':
    main()
