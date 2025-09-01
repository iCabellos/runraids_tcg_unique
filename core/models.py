from django.db import models
from django.db.models import Q
from django.contrib.auth.hashers import make_password
from django.utils.timezone import now
import math


# =============================================================
#  ENUMS Y CONSTANTES BÁSICAS
# =============================================================

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


# --- Sistema de héroes: taxonomías --- #
class HeroPrimaryMechanic(models.TextChoices):
    COMBAT = 'combat', 'Combate'
    GATHERING = 'gathering', 'Recolección'
    CONSTRUCTION = 'construction', 'Construcción'


class DamageProfile(models.TextChoices):
    PHYSICAL = 'physical', 'Físico'
    MAGICAL = 'magical', 'Mágico'
    MIXED = 'mixed', 'Mixto'


class CombatSubRole(models.TextChoices):
    DPS = 'dps', 'DPS Puro'
    SUBDPS = 'subdps', 'SubDPS (potenciador de daño)'
    SUPPORT = 'support', 'Soporte/Buffer'
    DEFENDER = 'defender', 'Defensivo/Tanque'
    HEALER = 'healer', 'Curandero'


class RaceChoices(models.TextChoices):
    ELF = 'elf', 'Elfo'
    ORC = 'orc', 'Orco'
    DWARF = 'dwarf', 'Enano'
    HUMAN = 'human', 'Humano'
    OGRE = 'ogre', 'Ogro'
    UNDEAD = 'undead', 'No-muerto'
    GOBLIN = 'goblin', 'Goblin'


class ClassChoices(models.TextChoices):
    MAGE = 'mage', 'Mago'
    WARRIOR = 'warrior', 'Guerrero'
    ROGUE = 'rogue', 'Pícaro'
    SHAMAN = 'shaman', 'Chamán'
    PRIEST = 'priest', 'Sacerdote'
    RANGER = 'ranger', 'Explorador/Arquero'


# --- Ataques/Habilidades: enums atómicos para rellenar opciones en base al tipo --- #
class SkillEffectType(models.TextChoices):
    DAMAGE = 'damage', 'Daño'
    HEAL = 'heal', 'Curación'
    BUFF = 'buff', 'Mejora (buff)'
    DEBUFF = 'debuff', 'Perjuicio (debuff)'


class SkillTarget(models.TextChoices):
    SELF = 'self', 'Sí mismo'
    ALLY_SINGLE = 'ally_single', 'Aliado objetivo'
    ALLY_TEAM = 'ally_team', 'Equipo aliado'
    ENEMY_SINGLE = 'enemy_single', 'Enemigo objetivo'
    ENEMY_TEAM = 'enemy_team', 'Equipo enemigo (AoE)'


class SkillSlot(models.TextChoices):
    BASIC = 'basic', 'Ataque básico (suma ira)'
    ULTIMATE = 'ultimate', 'Ulti (consume ira)'
    PASSIVE_1 = 'passive_1', 'Pasiva 1'
    PASSIVE_2 = 'passive_2', 'Pasiva 2'


class ScalingStat(models.TextChoices):
    NONE = 'none', 'Sin escalado'
    ATK_PHY = 'atk_phy', 'Ataque físico'
    ATK_MAG = 'atk_mag', 'Ataque mágico'
    HP = 'hp', 'Vida'
    DEF_PHY = 'def_phy', 'Defensa física'
    DEF_MAG = 'def_mag', 'Defensa mágica'
    SPEED = 'speed', 'Velocidad'


class PassiveTrigger(models.TextChoices):
    ALWAYS = 'always', 'Siempre activo'
    ON_HIT = 'on_hit', 'Al golpear'
    ON_KILL = 'on_kill', 'Al matar'
    ON_DAMAGED = 'on_damaged', 'Al recibir daño'
    ON_BATTLE_START = 'on_battle_start', 'Al empezar el combate'


class SubstatType(models.TextChoices):
    # Combate general
    BONUS_ATK_PHY = 'bonus_atk_phy', '% Ataque físico'
    BONUS_ATK_MAG = 'bonus_atk_mag', '% Ataque mágico'
    BONUS_HP = 'bonus_hp', '% Vida'
    BONUS_DEF_PHY = 'bonus_def_phy', '% Defensa física'
    BONUS_DEF_MAG = 'bonus_def_mag', '% Defensa mágica'
    BONUS_SPEED = 'bonus_speed', '% Velocidad'
    CRIT_CHANCE = 'crit_chance', '% Prob. crítico'
    CRIT_DAMAGE = 'crit_damage', '% Daño crítico'
    HEAL_BONUS = 'heal_bonus', '% Bonificación de curación'
    RAGE_START = 'rage_start', 'Ira inicial (valor absoluto)'
    RAGE_ON_HIT = 'rage_on_hit', 'Ira al golpear (valor absoluto)'

    # Recolección / Construcción
    GATHER_SPEED_GLOBAL = 'gather_speed_global', '% Velocidad de recolección (global)'
    GATHER_YIELD_GLOBAL = 'gather_yield_global', '% Rendimiento de recolección (global)'
    CONSTRUCTION_SPEED = 'construction_speed', '% Velocidad de construcción'
    # Específicos por recurso (usar con resource_type opcional)
    GATHER_SPEED_RESOURCE = 'gather_speed_resource', '% Vel. recolección por recurso'
    GATHER_YIELD_RESOURCE = 'gather_yield_resource', '% Rendimiento por recurso'


class ArtifactSlot(models.TextChoices):
    WEAPON = 'weapon', 'Arma'
    NECKLACE = 'necklace', 'Collar'
    RING = 'ring', 'Anillo'


# =============================================================
#  USUARIOS / AMISTADES / ALIANZAS
# =============================================================

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

    def create_default_buildings(self):
        from core.models import BuildingType, PlayerBuilding
        for type_choice, name in BuildingTypeChoices.choices:
            BuildingType.objects.get_or_create(type=type_choice, defaults={"name": name})
        camp_type = BuildingType.objects.get(type=BuildingTypeChoices.CAMP)
        PlayerBuilding.objects.get_or_create(member=self, building_type=camp_type, defaults={"level": 1})

    def __str__(self):
        return f'Member: {self.id}, {self.name}'


class FriendRequest(models.Model):
    """Tabla 1: solicitudes de amistad (1:N), con flag de aceptación."""
    sender = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='sent_requests')
    receiver = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='received_requests')
    accepted = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=now)

    class Meta:
        unique_together = ('sender', 'receiver')
        constraints = [
            models.CheckConstraint(check=~Q(sender=models.F('receiver')), name='friendrequest_no_self')
        ]

    def __str__(self):
        status = 'aceptada' if self.accepted else 'pendiente'
        return f"Solicitud {self.sender.name} → {self.receiver.name} ({status})"


class Friendship(models.Model):
    """Tabla 2: relación de amistad final (1:1 por par de usuarios)."""
    member_a = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='friendships_a')
    member_b = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='friendships_b')
    from_request = models.OneToOneField(FriendRequest, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(default=now)

    class Meta:
        unique_together = ('member_a', 'member_b')
        constraints = [
            models.CheckConstraint(check=~Q(member_a=models.F('member_b')), name='friendship_no_self')
        ]

    def save(self, *args, **kwargs):
        # Normaliza el par para evitar duplicados invertidos (a,b) vs (b,a)
        if self.member_b_id and self.member_a_id and self.member_b_id < self.member_a_id:
            self.member_a_id, self.member_b_id = self.member_b_id, self.member_a_id
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.member_a.name} 🤝 {self.member_b.name}"


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


# =============================================================
#  CIUDAD Y RECURSOS
# =============================================================

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


# =============================================================
#  HABILIDADES / ATAQUES (definiciones)
# =============================================================

class Skill(models.Model):
    """
    Definición de una habilidad/ataque.
    Selecciona el tipo mediante enums (effect_type, target, scaling_stat, damage_profile) y rellena los
    campos numéricos adecuados según aplique (base_value para daños/curas, percent_value para buff/debuff).

    La selección de qué habilidad usar se decide en tiempo de combate (fuera de estos modelos).
    """
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, default='')

    effect_type = models.CharField(max_length=10, choices=SkillEffectType.choices)
    target = models.CharField(max_length=20, choices=SkillTarget.choices, default=SkillTarget.ENEMY_SINGLE)
    damage_profile = models.CharField(max_length=10, choices=DamageProfile.choices, default=DamageProfile.MIXED)
    scaling_stat = models.CharField(max_length=12, choices=ScalingStat.choices, default=ScalingStat.NONE)

    # Valores base
    base_value = models.FloatField(
        default=0.0,
        help_text="Daño/Curación base (valor absoluto). Para BUFF/DEBUFF usa percent_value."
    )
    percent_value = models.FloatField(
        default=0.0,
        help_text="Porcentaje para BUFF/DEBUFF (0.20 = +20%)."
    )

    # Pasivas
    passive_trigger = models.CharField(max_length=20, choices=PassiveTrigger.choices, default=PassiveTrigger.ALWAYS)

    # Ira (básico suele ganar; ulti suele consumir)
    rage_gain = models.IntegerField(default=0)
    rage_cost = models.IntegerField(default=0)

    # Progresión por dupes (+20% por nivel por defecto)
    per_level_multiplier = models.FloatField(default=0.20)
    max_level = models.PositiveIntegerField(default=5)

    created_at = models.DateTimeField(default=now)

    def __str__(self):
        return self.name


# =============================================================
#  HÉROES
# =============================================================

class Rarity(models.Model):
    type = models.CharField(max_length=50, choices=[
        ('common', 'Common'),
        ('rare', 'Rare'),
        ('epic', 'Epic'),
        ('legendary', 'Legendary'),
    ], default='common')

    def __str__(self):
        return self.type


class Hero(models.Model):
    """Héroe base. TODOS tienen 4 habilidades: basic, ultimate, passive_1, passive_2."""
    # Identidad
    codename = models.SlugField(max_length=40, unique=True, help_text="Nombre corto y único (una sola palabra)")
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, default='')
    image = models.ImageField(upload_to='heroes/', blank=True, null=True)

    # Taxonomía
    race = models.CharField(max_length=20, choices=RaceChoices.choices)
    klass = models.CharField(max_length=20, choices=ClassChoices.choices)
    rarity = models.ForeignKey(Rarity, on_delete=models.CASCADE, null=True, blank=True, default=None)

    primary_mechanic = models.CharField(max_length=20, choices=HeroPrimaryMechanic.choices, default=HeroPrimaryMechanic.COMBAT)
    damage_profile = models.CharField(max_length=10, choices=DamageProfile.choices, default=DamageProfile.MIXED)
    subrole = models.CharField(max_length=20, choices=CombatSubRole.choices, blank=True, null=True)

    # Stats base (nivel 1)
    base_hp = models.IntegerField(default=50)
    base_atk_mag = models.IntegerField(default=10)
    base_atk_phy = models.IntegerField(default=10)
    base_def_mag = models.IntegerField(default=10)
    base_def_phy = models.IntegerField(default=10)
    base_speed = models.IntegerField(default=10)
    base_crit_chance = models.FloatField(default=0.05, help_text="Prob. crítico base (0.05 = 5%)")
    base_crit_damage = models.FloatField(default=1.50, help_text="Multiplicador de daño crítico (1.5 = 150%)")

    # Ira
    rage_max = models.IntegerField(default=100)
    starting_rage = models.IntegerField(default=0)

    # Relación con habilidades (a través para fijar slots obligatorios)
    skills = models.ManyToManyField("Skill", through='HeroSkill', related_name="heroes")

    created_at = models.DateTimeField(default=now)

    def __str__(self):
        return f"{self.name} ({self.codename})"


class HeroSkill(models.Model):
    """Asignación de habilidades a un héroe y su slot obligatorio (basic/ultimate/pasivas)."""
    hero = models.ForeignKey(Hero, on_delete=models.CASCADE)
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    slot = models.CharField(max_length=12, choices=SkillSlot.choices)

    # Overrides opcionales por héroe (si difieren de la definición base)
    rage_gain_override = models.IntegerField(blank=True, null=True)
    rage_cost_override = models.IntegerField(blank=True, null=True)

    class Meta:
        unique_together = ('hero', 'slot')

    def __str__(self):
        return f"{self.hero.codename} - {self.get_slot_display()} - {self.skill.name}"

    @property
    def effective_rage_gain(self):
        return self.rage_gain_override if self.rage_gain_override is not None else self.skill.rage_gain

    @property
    def effective_rage_cost(self):
        return self.rage_cost_override if self.rage_cost_override is not None else self.skill.rage_cost


# NUEVO: curva de experiencia híbrida (anclas + crecimiento suave)
class ExperienceCurve:
    """
    Anclas:
      - L2 = 5 XP, L3 = 40 XP, L4 = 100 XP (acumulada)
    Objetivo:
      - L100 ≈ 1000 XP total (≈ 200 ovejas × 5 XP)
    De L>=5 en adelante: crecimiento por potencia suavizada.
    """
    MAX_LEVEL = 100

    _anchors = {
        1: 0.0,
        2: 5.0,
        3: 40.0,
        4: 100.0,
    }

    _target_total_at_100 = 1000.0
    _p = 1.45  # exponente suave

    @classmethod
    def cumulative_xp_for_level(cls, level: int) -> int:
        """XP acumulada necesaria para ALCANZAR el nivel (mínimo 1)."""
        if level <= 1:
            return 0
        if level in cls._anchors:
            return int(cls._anchors[level])
        # Normalización a partir de L5 para llegar a ~1000 en L100
        k = 900.0 / (96.0 ** cls._p)  # 1000 - 100 = 900; 100 ↔ L4
        if level >= cls.MAX_LEVEL:
            level = cls.MAX_LEVEL
        val = 100.0 + k * ((level - 4) ** cls._p)
        return int(val)

    @classmethod
    def level_from_xp(cls, xp: int) -> int:
        """Nivel derivado a partir de XP acumulada (cap en MAX_LEVEL)."""
        xp = max(0, int(xp))
        lo, hi = 1, cls.MAX_LEVEL
        # búsqueda binaria
        while lo < hi:
            mid = (lo + hi + 1) // 2
            if cls.cumulative_xp_for_level(mid) <= xp:
                lo = mid
            else:
                hi = mid - 1
        return lo

    @classmethod
    def next_level_xp(cls, level: int) -> int:
        """XP acumulada necesaria para el siguiente nivel (o el cap)."""
        if level >= cls.MAX_LEVEL:
            return cls.cumulative_xp_for_level(cls.MAX_LEVEL)
        return cls.cumulative_xp_for_level(level + 1)


class PlayerHero(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    hero = models.ForeignKey(Hero, on_delete=models.CASCADE)

    # Progresión: el nivel se deriva de 'experience'
    experience = models.IntegerField(default=0)

    created_at = models.DateTimeField(default=now)

    class Meta:
        unique_together = ('member', 'hero')

    def __str__(self):
        return f'{self.member.name} - {self.hero.name} lvl {self.level}'

    # ---- Nivel efectivo (derivado) con cap por HQ ----
    @property
    def level(self) -> int:
        base_level = ExperienceCurve.level_from_xp(self.experience)
        return min(base_level, self.max_level_cap)

    @property
    def max_level_cap(self) -> int:
        hq = PlayerBuilding.objects.filter(
            member=self.member,
            building_type__type=BuildingTypeChoices.HQ
        ).first()
        return hq.level * 5 + 5 if hq else 10

    @property
    def next_level_required_xp(self) -> int:
        """Umbral acumulado para el siguiente nivel efectivo (considerando cap)."""
        current = self.level
        target_level = min(current + 1, self.max_level_cap)
        return ExperienceCurve.cumulative_xp_for_level(target_level)

    @property
    def xp_to_next_level(self) -> int:
        """XP restante para subir al siguiente nivel efectivo."""
        if self.level >= self.max_level_cap:
            return 0
        needed = ExperienceCurve.cumulative_xp_for_level(self.level + 1)
        return max(0, needed - int(self.experience))

    def add_experience(self, amount: int) -> None:
        """Suma XP (la lógica de combate/registro está fuera del modelo)."""
        if amount > 0:
            self.experience = int(self.experience) + int(amount)
            self.save(update_fields=["experience"])

    # ---- Escalado de stats base: +5% lineal por nivel (no afecta críticos/curas, etc.) ----
    def _stat_multiplier(self) -> float:
        # Lineal sobre el valor base del héroe (no compuesto): 1 + 0.05*(nivel-1)
        return 1.0 + 0.05 * max(self.level - 1, 0)

    def s_hp(self) -> int:
        return int(self.hero.base_hp * self._stat_multiplier())

    def s_atk_mag(self) -> int:
        return int(self.hero.base_atk_mag * self._stat_multiplier())

    def s_atk_phy(self) -> int:
        return int(self.hero.base_atk_phy * self._stat_multiplier())

    def s_def_mag(self) -> int:
        return int(self.hero.base_def_mag * self._stat_multiplier())

    def s_def_phy(self) -> int:
        return int(self.hero.base_def_phy * self._stat_multiplier())

    def s_speed(self) -> int:
        return int(self.hero.base_speed * self._stat_multiplier())

class PlayerHeroSkill(models.Model):
    """Estado por jugador de cada habilidad del héroe (niveles por dupes)."""
    player_hero = models.ForeignKey(PlayerHero, on_delete=models.CASCADE, related_name='skills')
    hero_skill = models.ForeignKey(HeroSkill, on_delete=models.CASCADE)

    level = models.PositiveIntegerField(default=1)
    dupes_spent = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('player_hero', 'hero_skill')

    def __str__(self):
        return f"{self.player_hero} - {self.hero_skill.get_slot_display()} lvl {self.level}"

    def effective_base_value(self) -> float:
        base = self.hero_skill.skill.base_value
        mult = self.hero_skill.skill.per_level_multiplier
        return float(base) * (1.0 + mult * (self.level - 1))

    def effective_percent(self) -> float:
        perc = self.hero_skill.skill.percent_value
        mult = self.hero_skill.skill.per_level_multiplier
        return float(perc) * (1.0 + mult * (self.level - 1))


# =============================================================
#  ARTEFACTOS / EQUIPO (substats vienen del equipo, no los define el jugador)
# =============================================================

class Artifact(models.Model):
    name = models.CharField(max_length=100)
    slot = models.CharField(max_length=20, choices=ArtifactSlot.choices)
    rarity = models.ForeignKey(Rarity, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField(blank=True, default='')
    image = models.ImageField(upload_to='artifacts/', blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.get_slot_display()})"


class ArtifactSubstat(models.Model):
    artifact = models.ForeignKey(Artifact, on_delete=models.CASCADE, related_name='substats')
    substat_type = models.CharField(max_length=40, choices=SubstatType.choices)
    value = models.FloatField(default=0.0)
    resource_type = models.ForeignKey(ResourceType, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        scope = f" ({self.resource_type.name})" if self.resource_type else ""
        return f"{self.artifact.name} - {self.get_substat_type_display()}{scope}: {self.value}"


class PlayerArtifact(models.Model):
    owner = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='artifacts')
    artifact = models.ForeignKey(Artifact, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=now)

    def __str__(self):
        return f"{self.owner.name} - {self.artifact.name}"


class PlayerHeroEquipment(models.Model):
    player_hero = models.ForeignKey(PlayerHero, on_delete=models.CASCADE, related_name='equipment')
    player_artifact = models.ForeignKey(PlayerArtifact, on_delete=models.CASCADE)
    slot = models.CharField(max_length=20, choices=ArtifactSlot.choices)
    equipped_at = models.DateTimeField(default=now)

    class Meta:
        unique_together = (
            ('player_hero', 'slot'),  # un artefacto por slot
        )

    def __str__(self):
        return f"{self.player_hero} → {self.get_slot_display()} = {self.player_artifact.artifact.name}"


# =============================================================
#  ENEMIGOS (mantenidos, sin lógica de combate)
# =============================================================

class Enemy(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='enemies/', blank=True, null=True)
    description = models.TextField(blank=True)
    level = models.IntegerField(default=1)
    base_hp = models.IntegerField()
    attack = models.IntegerField()
    defense = models.IntegerField()
    speed = models.IntegerField()
    skills = models.ManyToManyField("Skill", blank=True)
    created_at = models.DateTimeField(default=now)

    def __str__(self):
        return f'{self.name} (lvl {self.level})'
