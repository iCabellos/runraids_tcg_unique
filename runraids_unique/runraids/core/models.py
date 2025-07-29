from datetime import timezone
from django.db import models
from django.contrib.auth.hashers import make_password
from django.utils.timezone import now


### --- ENUM para tipo de edificio --- ###
class BuildingTypeChoices(models.TextChoices):
    HQ = 'hq', 'Edificio principal'
    XP_HERO = 'xp_tower_heroes', 'Edificio de gestión para héroes'
    XP_FARM = 'xp_farming', 'Edificio almacenador de experiéncia'
    MARKET = 'market', 'Mercado'
    ALLIANCE = 'alliance', 'Centro de la alianza'


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
        if not self.password_member.startswith("pbkdf2_sha256$"):
            self.password_member = make_password(self.password_member)
        super().save(*args, **kwargs)

    def __str__(self):
        return f'Member: {self.id}, {self.name}'


### --- CIUDAD Y RECURSOS --- ###
class BuildingType(models.Model):
    name = models.CharField(max_length=100)
    type = models.CharField(
        max_length=50,
        choices=BuildingTypeChoices.choices,
        unique=True
    )
    image = models.ImageField(
        upload_to='buildings/',
        blank=True,
        null=True,
        help_text="Imagen PNG con fondo transparente que represente este tipo de edificio"
    )

    def __str__(self):
        return self.name


class ResourceType(models.Model):
    name = models.CharField(max_length=100)  # ej: oro, comida, cristal
    description = models.TextField()

    def __str__(self):
        return self.name


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
    stored_xp = models.FloatField(default=0)

    @property
    def xp_rate(self):
        # XP por segundo: 1 + 0.5 * (nivel - 1)
        return round(1 + 0.5 * (self.level - 1), 1)

    def __str__(self):
        return f'{self.member.name} - {self.building_type.name} (Lv. {self.level})'


### --- HÉROES Y HABILIDADES --- ###
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
    current_hp = models.IntegerField()
    exp = models.IntegerField(default=0)

    def get_level(self):
        return min(100, int((self.exp / 100) ** 0.6))

    @property
    def max_level(self):
        hq = PlayerBuilding.objects.filter(member=self.member, building_type__type=BuildingTypeChoices.HQ).first()
        if hq:
            return hq.level * 5 + 5
        return 10

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
