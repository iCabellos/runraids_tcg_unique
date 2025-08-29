"""
URL configuration for runraids project - Vercel deployment.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
"""
import os
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from api.views import index as test_index

# Try to import core views, fallback to test view if not available
try:
    from core.views import IndexView, DashboardView, CombatView, logout_view, CityView, CampView
    core_available = True
except ImportError:
    core_available = False

urlpatterns = [
    path('admin/', admin.site.urls),
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
    # Fallback to test view if core is not available
    urlpatterns += [
        path('', test_index, name="test_index"),
    ]

# Static and media files
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
