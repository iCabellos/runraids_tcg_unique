"""
URL configuration for runraids project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import os
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from core.views import IndexView, DashboardView, CombatView, logout_view, CityView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', IndexView.as_view(), name="index"),
    path('userprofile/', DashboardView.as_view(), name="userprofile"),
    path('combat/', CombatView.as_view(), name="combat"),
    path('city/', CityView.as_view(), name="city"),
    path('logout/', logout_view, name="logout"),
]


urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
if settings.DEBUG:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    urlpatterns += static(settings.STATIC_URL, document_root=os.path.join(BASE_DIR, '/static'))
