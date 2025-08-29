"""
WSGI config for runraids project - Vercel deployment.

It exposes the WSGI callable as a module-level variable named ``app``.
This is required by Vercel's Python runtime.
"""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'api.settings')

# Vercel requires the WSGI application to be named 'app'
app = get_wsgi_application()
