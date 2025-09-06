from django.contrib import admin
from core.models import (
    Member,
    ResourceType,
    PlayerResource,
    BuildingType,
    BuildingLevelCost,
    PlayerBuilding,
    Rarity,
    Skill,
    Hero,
    Enemy,
    PlayerHero,
    Alliance,
    AllianceMember,
    AllianceSettings,
    AllianceBuilding,
    Friendship,
    Banner,
    BannerEntry,
    BannerReward,
    BannerRewardItem,
    Raid,
    RaidWave,
    RaidEnemy,
    RaidRoom,
    Team,
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


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ("name", "effect_type", "target", "damage_profile", "rage_gain", "rage_cost")
    list_filter = ("effect_type", "target", "damage_profile")
    search_fields = ("name",)


@admin.register(Rarity)
class AbilityAdmin(admin.ModelAdmin):
    list_display = ("type",)


@admin.register(Hero)
class HeroAdmin(admin.ModelAdmin):
    list_display = ("name", "base_hp", "base_atk_mag", "base_def_mag", "base_speed")
    search_fields = ("name", "codename")


@admin.register(Enemy)
class EnemyAdmin(admin.ModelAdmin):
    list_display = ("name", "base_hp", "attack", "defense", "speed")
    search_fields = ("name",)


@admin.register(PlayerHero)
class PlayerHeroAdmin(admin.ModelAdmin):
    list_display = ("member", "hero", "level", "experience")
    search_fields = ("member__name", "hero__name")




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
    list_display = ("member_a", "member_b", "created_at")
    search_fields = ("member_a__name", "member_b__name")


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ("name", "starts_at", "is_active")


@admin.register(BannerEntry)
class BannerEntryAdmin(admin.ModelAdmin):
    list_display = ("banner", "hero", "is_promotional")


@admin.register(BannerReward)
class BannerRewardAdmin(admin.ModelAdmin):
    list_display = ("banner", "name")


@admin.register(BannerRewardItem)
class BannerRewardItemAdmin(admin.ModelAdmin):
    list_display = ("reward", "resource_type", "min_amount", "max_amount")


# ====== RAIDS ======
@admin.register(Raid)
class RaidAdmin(admin.ModelAdmin):
    list_display = ("name", "difficulty", "min_players", "max_players", "created_at")
    list_filter = ("difficulty",)
    search_fields = ("name",)


class RaidEnemyInline(admin.TabularInline):
    model = RaidEnemy
    extra = 1


@admin.register(RaidWave)
class RaidWaveAdmin(admin.ModelAdmin):
    list_display = ("raid", "wave_number", "name")
    list_filter = ("raid",)
    ordering = ("raid", "wave_number")
    inlines = [RaidEnemyInline]


@admin.register(RaidEnemy)
class RaidEnemyAdmin(admin.ModelAdmin):
    list_display = ("wave", "enemy", "quantity", "level_modifier")
    list_filter = ("wave__raid", "enemy")


@admin.register(RaidRoom)
class RaidRoomAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "raid", "owner", "state", "max_players", "created_at")
    list_filter = ("state", "raid")
    search_fields = ("name", "owner__name")


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ("id", "owner", "name", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("owner__name", "name")
