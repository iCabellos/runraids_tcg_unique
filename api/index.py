# api/index.py
import os
from vercel_wsgi import handle
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "api.settings")

# Django WSGI app
application = get_wsgi_application()

# Vercel busca `handler` o `app`. Aquí exponemos `handler`.
def handler(request, context):
    return handle(request, application)
