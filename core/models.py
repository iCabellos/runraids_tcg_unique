from django.db import models
from django.contrib.auth.hashers import make_password
from django.utils.timezone import now


### --- ENUM para tipo de edificio --- ###
class BuildingTypeChoices(models.TextChoices):
    # Main building for alliance
    HQ = 'hq', 'Edificio principal'
    XP_HERO = 'xp_tower_heroes', 'Edificio de gestión para héroes'
    XP_FARM = 'xp_farming', 'Edificio almacenador de experiéncia'
    MARKET = 'market', 'Mercado'
    ALLIANCE = 'alliance', 'Centro de la alianza'
    # Main building for players
    CAMP = 'camp', 'Campamento principal'
    CAMPFIRE = 'cf', 'Hoguera'
    STORAGE = 'store', 'Alijo principal'
    WC_PORTAL = 'wc_portal', 'Baño invocador'


### --- USUARIO --- ###
class Member(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    firstname = models.CharField(max_length=255)
    password_member = models.CharField(max_length=128)
    email = models.EmailField(max_length=255)
    phone = models.IntegerField()
    created_at = models.DateTimeField(default=now)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Hash password if it's not already hashed
        if not self.password_member.startswith("pbkdf2_sha256$"):
            self.password_member = make_password(self.password_member)

        # Just save the member - building creation will be handled elsewhere
        super().save(*args, **kwargs)

    def create_default_buildings(self):
        """Create default buildings for this member. Call this after member is saved."""
        # Import here to avoid circular import
        from core.models import BuildingType, PlayerBuilding

        # Ensure building types exist
        for type_choice, name in BuildingTypeChoices.choices:
            BuildingType.objects.get_or_create(type=type_choice, defaults={"name": name})

        # Create default camp building if it doesn't exist
        camp_type = BuildingType.objects.get(type=BuildingTypeChoices.CAMP)
        PlayerBuilding.objects.get_or_create(member=self, building_type=camp_type, defaults={"level": 1})

    def __str__(self):
        return f'Member: {self.id}, {self.name}'


class Friendship(models.Model):
    sender = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='sent_requests')
    receiver = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='received_requests')
    accepted = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=now)

    class Meta:
        unique_together = ('sender', 'receiver')


### --- ALIANZAS --- ###
class Alliance(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(default=now)

    def __str__(self):
        return self.name


class AllianceMember(models.Model):
    ROLE_CHOICES = [
        ('leader', 'Líder'),
        ('co_leader', 'Co-líder'),
        ('officer', 'Oficial'),
        ('member', 'Miembro'),
    ]
    alliance = models.ForeignKey(Alliance, on_delete=models.CASCADE, related_name='memberships')
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='alliances')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member')
    joined_at = models.DateTimeField(default=now)

    class Meta:
        unique_together = ('alliance', 'member')

    def __str__(self):
        return f"{self.member.name} - {self.get_role_display()} in {self.alliance.name}"


class AllianceSettings(models.Model):
    alliance = models.OneToOneField(Alliance, on_delete=models.CASCADE, related_name='settings')
    open_to_join = models.BooleanField(default=False)
    description = models.TextField(blank=True)
    raid_notifications = models.BooleanField(default=True)
    custom_rules = models.TextField(blank=True)

    def __str__(self):
        return f"Ajustes de {self.alliance.name}"


### --- CIUDAD Y RECURSOS --- ###
class BuildingType(models.Model):
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=50, choices=BuildingTypeChoices.choices, unique=True)
    image = models.ImageField(upload_to='buildings/', blank=True, null=True)

    def __str__(self):
        return self.name


class ResourceType(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.name


class BuildingLevelCost(models.Model):
    building_type = models.ForeignKey(BuildingType, on_delete=models.CASCADE, related_name='level_costs')
    level = models.PositiveIntegerField()
    resource_type = models.ForeignKey(ResourceType, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField()

    class Meta:
        unique_together = ('building_type', 'level', 'resource_type')

    def __str__(self):
        return f"{self.building_type.name} - Lvl {self.level} - {self.resource_type.name}: {self.amount}"


class PlayerResource(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    resource_type = models.ForeignKey(ResourceType, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f'{self.member.name} - {self.resource_type.name}: {self.amount}'


class PlayerBuilding(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    building_type = models.ForeignKey(BuildingType, on_delete=models.CASCADE, null=True)
    level = models.IntegerField(default=1)

    def get_upgrade_cost(self):
        return BuildingLevelCost.objects.filter(
            building_type=self.building_type,
            level=self.level + 1
        )

    def __str__(self):
        return f'{self.member.name} - {self.building_type.name} (Lv. {self.level})'



class AllianceBuilding(models.Model):
    alliance = models.ForeignKey(Alliance, on_delete=models.CASCADE, related_name='buildings')
    building_type = models.ForeignKey(BuildingType, on_delete=models.CASCADE)
    level = models.IntegerField(default=1)

    def __str__(self):
        return f'{self.alliance.name} - {self.building_type.name} (Lv. {self.level})'


### --- HÉROES Y HABILIDADES --- ###
class Rarity(models.Model):
    type = models.CharField(max_length=50, choices=[
        ('common', 'Common'),
        ('rare', 'Rare'),
        ('epic', 'Epic'),
        ('legendary', 'Legendary'),
    ], default='common')

    def __str__(self):
        return self.type


class Ability(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    type = models.CharField(max_length=50, choices=[
        ('damage', 'Damage'),
        ('heal', 'Heal'),
        ('buff', 'Buff'),
        ('debuff', 'Debuff'),
    ])
    power = models.IntegerField()

    def __str__(self):
        return self.name


class Hero(models.Model):
    name = models.CharField(max_length=100)
    rarity = models.ForeignKey(Rarity, on_delete=models.CASCADE, null=True, blank=True, default=None)
    image = models.ImageField(upload_to='heroes/', blank=True, null=True)
    description = models.TextField()
    base_hp = models.IntegerField()
    base_attack = models.IntegerField(default=50)
    base_defense = models.IntegerField(default=30)
    base_speed = models.IntegerField(default=30)
    abilities = models.ManyToManyField("Ability", related_name="heroes")

    def __str__(self):
        return self.name


class PlayerHero(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    hero = models.ForeignKey(Hero, on_delete=models.CASCADE)
    current_hp = models.IntegerField(default=100)  # Default HP
    level = models.IntegerField(default=1)  # Add level field
    experience = models.IntegerField(default=0)  # Rename exp to experience

    def get_level(self):
        return self.level  # Use the level field directly

    @property
    def max_level(self):
        hq = PlayerBuilding.objects.filter(member=self.member, building_type__type=BuildingTypeChoices.HQ).first()
        return hq.level * 5 + 5 if hq else 10

    def get_scaled_stat(self, base_value):
        return int(base_value + (base_value * 0.1 * self.get_level()))

    def get_attack(self):
        return self.get_scaled_stat(self.hero.base_attack)

    def get_defense(self):
        return self.get_scaled_stat(self.hero.base_defense)

    def get_speed(self):
        return self.get_scaled_stat(self.hero.base_speed)

    def __str__(self):
        return f'{self.member.name} - {self.hero.name} lvl {self.get_level()}'


class Enemy(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='enemies/', blank=True, null=True)
    description = models.TextField(blank=True)
    level = models.IntegerField(default=1)
    base_hp = models.IntegerField()
    attack = models.IntegerField()
    defense = models.IntegerField()
    speed = models.IntegerField()
    abilities = models.ManyToManyField("Ability", blank=True)
    created_at = models.DateTimeField(default=now)

    def __str__(self):
        return f'{self.name} (lvl {self.level})'


### --- RAIDS --- ###
class RaidEvent(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    enemy_name = models.CharField(max_length=100)
    enemy_hp = models.IntegerField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    def __str__(self):
        return f'Raid: {self.name}'


class RaidParticipation(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    raid = models.ForeignKey(RaidEvent, on_delete=models.CASCADE)
    damage_done = models.IntegerField(default=0)
    joined_at = models.DateTimeField(default=now)

    def __str__(self):
        return f'{self.member.name} in {self.raid.name}'
