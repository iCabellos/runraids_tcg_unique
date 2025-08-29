# api/server.py
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "api.settings")

# Vercel busca exactamente `app` o `handler` a nivel módulo:
app = get_wsgi_application()
