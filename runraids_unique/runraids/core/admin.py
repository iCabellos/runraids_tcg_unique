from django.contrib import admin
from core.models import (
    Member,
    ResourceType,
    PlayerResource,
    BuildingType,
    PlayerBuilding,
    Ability,
    Hero,
    Enemy,
    PlayerHero,
    RaidEvent,
    RaidParticipation
)


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "email", "phone")
    search_fields = ("name", "email")


@admin.register(ResourceType)
class ResourceTypeAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "description")


@admin.register(PlayerResource)
class PlayerResourceAdmin(admin.ModelAdmin):
    list_display = ("member", "resource_type", "amount")


@admin.register(BuildingType)
class BuildingTypeAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "type")
    list_filter = ("type",)
    search_fields = ("name",)


@admin.register(PlayerBuilding)
class PlayerBuildingAdmin(admin.ModelAdmin):
    list_display = ("member", "building_type", "level", "stored_xp")
    list_filter = ("building_type__type",)
    search_fields = ("member__name",)


@admin.register(Ability)
class AbilityAdmin(admin.ModelAdmin):
    list_display = ("name", "type", "power")
    list_filter = ("type",)
    search_fields = ("name",)


@admin.register(Hero)
class HeroAdmin(admin.ModelAdmin):
    list_display = ("name", "base_hp", "base_attack", "base_defense", "base_speed")
    filter_horizontal = ("abilities",)
    search_fields = ("name",)


@admin.register(Enemy)
class EnemyAdmin(admin.ModelAdmin):
    list_display = ("name", "base_hp", "attack", "defense", "speed")
    filter_horizontal = ("abilities",)
    search_fields = ("name",)


@admin.register(PlayerHero)
class PlayerHeroAdmin(admin.ModelAdmin):
    list_display = ("member", "hero", "current_hp", "exp")
    search_fields = ("member__name", "hero__name")


@admin.register(RaidEvent)
class RaidEventAdmin(admin.ModelAdmin):
    list_display = ("name", "enemy_name", "start_time", "end_time")


@admin.register(RaidParticipation)
class RaidParticipationAdmin(admin.ModelAdmin):
    list_display = ("member", "raid", "damage_done", "joined_at")
    search_fields = ("member__name", "raid__name")
