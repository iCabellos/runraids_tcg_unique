from django.contrib import admin
from core.models import (
    Member,
    ResourceType,
    PlayerResource,
    BuildingType,
    BuildingLevelCost,
    PlayerBuilding,
    Rarity,
    Ability,
    Hero,
    Enemy,
    PlayerHero,
    RaidEvent,
    RaidParticipation,
    Alliance,
    AllianceMember,
    AllianceSettings,
    AllianceBuilding,
    Friendship
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


@admin.register(BuildingLevelCost)
class BuildingLevelCostAdmin(admin.ModelAdmin):
    list_display = ("building_type", "level", "resource_type", "amount")
    list_filter = ("building_type", "level", "resource_type")
    search_fields = ("building_type__name", "resource_type__name")
    ordering = ("building_type", "level", "resource_type")


@admin.register(PlayerBuilding)
class PlayerBuildingAdmin(admin.ModelAdmin):
    list_display = ("member", "building_type", "level")
    list_filter = ("building_type__type",)
    search_fields = ("member__name",)


@admin.register(Ability)
class AbilityAdmin(admin.ModelAdmin):
    list_display = ("name", "type", "power")
    list_filter = ("type",)
    search_fields = ("name",)


@admin.register(Rarity)
class AbilityAdmin(admin.ModelAdmin):
    list_display = ("type",)


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
    list_display = ("member", "hero", "current_hp", "experience")
    search_fields = ("member__name", "hero__name")


@admin.register(RaidEvent)
class RaidEventAdmin(admin.ModelAdmin):
    list_display = ("name", "enemy_name", "start_time", "end_time")


@admin.register(RaidParticipation)
class RaidParticipationAdmin(admin.ModelAdmin):
    list_display = ("member", "raid", "damage_done", "joined_at")
    search_fields = ("member__name", "raid__name")


@admin.register(Alliance)
class AllianceAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "description", "created_at")
    search_fields = ("name",)


@admin.register(AllianceMember)
class AllianceMembershipAdmin(admin.ModelAdmin):
    list_display = ("member", "alliance", "role", "joined_at")
    list_filter = ("role",)
    search_fields = ("member__name", "alliance__name")


@admin.register(AllianceSettings)
class AllianceSettingsAdmin(admin.ModelAdmin):
    list_display = ("alliance", "open_to_join", "raid_notifications")


@admin.register(AllianceBuilding)
class AllianceBuildingAdmin(admin.ModelAdmin):
    list_display = ("alliance", "building_type", "level")


@admin.register(Friendship)
class FriendshipAdmin(admin.ModelAdmin):
    list_display = ("sender", "receiver", "accepted", "created_at")
    list_filter = ("accepted",)
    search_fields = ("sender__name", "receiver__name")
