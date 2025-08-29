import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "api.settings")

# WSGI estándar de Django
application = get_wsgi_application()

# 👇 Alias para Vercel (necesita `app` o `handler`)
app = application
handler = application
