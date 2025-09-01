"""
URL configuration for runraids project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
"""
from django.contrib import admin
from django.urls import path, re_path

# Try to import core views, fallback to simple view if not available
try:
    from core.views import IndexView, DashboardView, CombatView, logout_view, CityView, CampView
    core_available = True
except ImportError:
    core_available = False

from django.conf import settings
from django.views.static import serve as static_serve

urlpatterns = [
    path('admin/', admin.site.urls),
]

# Serve media files in all environments (note: on Vercel this serves from ephemeral storage)
urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', static_serve, {'document_root': settings.MEDIA_ROOT}),
]

if core_available:
    urlpatterns += [
        path('index/', IndexView.as_view(), name="index"),
        path('', CampView.as_view(), name="camp"),
        path('userprofile/', DashboardView.as_view(), name="userprofile"),
        path('combat/', CombatView.as_view(), name="combat"),
        path('alliance/', CityView.as_view(), name="alliance"),
        path('logout/', logout_view, name="logout"),
    ]
else:
    # Simple fallback view
    from django.http import HttpResponse
    def simple_view(request):
        return HttpResponse("RunRaids TCG - Core app not available")

    urlpatterns += [
        path('', simple_view, name="fallback"),
    ]
