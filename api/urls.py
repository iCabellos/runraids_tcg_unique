"""
URL configuration for runraids project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
"""
from django.contrib import admin
from django.urls import path, re_path

# Try to import core views, fallback to simple view if not available
try:
    from core import views as core_views
    from core.views import (
        IndexView, DashboardView, CombatView, logout_view, CityView, CampView, BannerView, MatchmakingView,
        api_pull, api_pull_multi, api_raid_matchmaking_join, api_raid_state, api_raid_decision,
        api_raids_available, api_raid_rooms_available, api_team_update
    )

    core_available = True
except ImportError:
    core_available = False

from django.conf import settings
from django.views.static import serve as static_serve
from core.services.pulls import perform_pull, PullError, InsufficientCurrency

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
        path('bathroom/', BannerView.as_view(), name="bathroom"),
        path('matchmaking/', MatchmakingView.as_view(), name="matchmaking"),
        path('matchmaking/room/<int:room_id>/', core_views.MatchmakingRoomView.as_view(), name="matchmaking_room"),
        path('raid/', core_views.RaidRoomPage.as_view(), name="raid_room"),
        path('raid/room/<int:room_id>/', core_views.RaidRoomDetailView.as_view(), name="raid_room_detail"),
        path('api/pull/<int:banner_id>/', lambda request, banner_id: api_pull(request, banner_id), name="api_pull"),
        path('api/pull/<int:banner_id>/multi/', lambda request, banner_id: api_pull_multi(request, banner_id), name="api_pull_multi"),
        path('api/raid/matchmaking/join/', api_raid_matchmaking_join, name="api_raid_matchmaking_join"),
        path('api/raid/state/<int:room_id>/', api_raid_state, name="api_raid_state"),
        path('api/raid/solo/start/', core_views.api_raid_solo_start, name="api_raid_solo_start"),
        path('api/raid/decision/', api_raid_decision, name="api_raid_decision"),
        path('api/raid/start/<int:room_id>/', core_views.api_raid_start, name="api_raid_start"),
        path('api/hero/heal/', core_views.api_hero_heal, name="api_hero_heal"),
        path('api/hero/heal/all/', core_views.api_hero_heal_all, name="api_hero_heal_all"),
        path('api/team/', core_views.api_team_get, name="api_team_get"),
        path('api/team/create/', core_views.api_team_create, name="api_team_create"),
        path('api/team/update/', api_team_update, name="api_team_update"),
        path('api/team/add/', core_views.api_team_add, name="api_team_add"),
        path('api/team/remove/', core_views.api_team_remove, name="api_team_remove"),
        path('api/raids/available/', api_raids_available, name="api_raids_available"),
        path('api/raid/rooms/available/', api_raid_rooms_available, name="api_raid_rooms_available"),
    ]
else:
    # Simple fallback view
    from django.http import HttpResponse
    def simple_view(request):
        return HttpResponse("RunRaids - Core app not available")

    urlpatterns += [
        path('', simple_view, name="fallback"),
    ]
