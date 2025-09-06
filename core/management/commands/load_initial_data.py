import json
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from django.db import models

# Try to import models, handle gracefully if not available
try:
    from core.models import (
        ResourceType, BuildingType, Rarity, Skill, SkillSlot, Hero, Enemy, Member,
        PlayerResource, PlayerHero, BuildingLevelCost, PlayerBuilding, HeroSkill,
        Raid, RaidWave, RaidEnemy
    )
    from django.contrib.auth.models import User

    models_available = True
except ImportError as e:
    models_available = False
    import_error = str(e)


class Command(BaseCommand):
    help = 'Load initial data from JSON file or directory'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before loading new data',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force reload even if data exists',
        )

    def handle(self, *args, **options):
        if not models_available:
            self.stdout.write(
                self.style.ERROR(f'Models not available: {import_error}')
            )
            self.stdout.write('Skipping initial data loading...')
            return

        # Detect new directory-based data layout first
        data_dir = os.path.join(settings.BASE_DIR, 'initial_data')
        data = {}

        def load_json_file(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error reading {path}: {e}'))
                return None

        if os.path.isdir(data_dir):
            self.stdout.write(f'📂 Loading initial data from directory: {data_dir}')
            # Expected files mapping: filename -> key in aggregated dict
            mapping = {
                'django_admin_users.json': 'django_admin_users',
                'members.json': 'test_users',
                'resource_types.json': 'resource_types',
                'building_types.json': 'building_types',
                'rarities.json': 'rarities',
                'abilities.json': 'abilities',
                'heroes.json': 'heroes',
                'enemies.json': 'enemies',
                'building_costs.json': 'building_costs',
                'raids.json': 'raids',
                'raid_waves.json': 'raid_waves',
                'raid_enemies.json': 'raid_enemies',
            }
            for filename, key in mapping.items():
                path = os.path.join(data_dir, filename)
                if os.path.exists(path):
                    payload = load_json_file(path)
                    if payload is not None:
                        data[key] = payload
                else:
                    data[key] = []
        else:
            # Fallback to legacy single-file layout
            json_file_path = os.path.join(settings.BASE_DIR, 'initial_data.json')
            if not os.path.exists(json_file_path):
                self.stdout.write(
                    self.style.WARNING(f'JSON file not found: {json_file_path}')
                )
                self.stdout.write('Skipping initial data loading...')
                return
            try:
                with open(json_file_path, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                self.stdout.write('📦 Loaded legacy initial_data.json')
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error reading JSON file: {e}')
                )
                return

        self.stdout.write('Loading initial data...')

        # Clear existing data if requested
        if options['clear']:
            self.stdout.write('🗑️  Clearing existing data...')
            try:
                # Clear in reverse order to avoid foreign key constraints
                PlayerHero.objects.all().delete()
                PlayerResource.objects.all().delete()
                BuildingLevelCost.objects.all().delete()
                Member.objects.all().delete()
                Hero.objects.all().delete()
                Enemy.objects.all().delete()
                Skill.objects.all().delete()
                Rarity.objects.all().delete()
                BuildingType.objects.all().delete()
                ResourceType.objects.all().delete()
                # Clear Django admin users except superusers created manually
                User.objects.filter(username__in=['admin']).delete()
                self.stdout.write('✅ Existing data cleared')
            except Exception as e:
                self.stdout.write(f'⚠️  Error clearing data: {e}')

        # Load Django Admin Users
        self.stdout.write('Loading Django admin users...')
        for admin_data in data.get('django_admin_users', []):
            user, created = User.objects.get_or_create(
                username=admin_data['username'],
                defaults={
                    'email': admin_data['email'],
                    'first_name': admin_data.get('first_name', ''),
                    'last_name': admin_data.get('last_name', ''),
                    'is_superuser': admin_data.get('is_superuser', False),
                    'is_staff': admin_data.get('is_staff', False)
                }
            )
            if created:
                user.set_password(admin_data['password'])
                user.save()
                self.stdout.write(f'Created Django admin user: {user.username}')
            else:
                # Non-destructive: do not overwrite existing admin users
                self.stdout.write(f'Skipped updating existing Django admin user: {user.username}')

        # Load Resource Types
        self.stdout.write('Loading resource types...')
        for resource_data in data.get('resource_types', []):
            resource_data.pop('pk', None)

            # Process image path for static files
            defaults = {'description': resource_data.get('description', '')}
            if 'image' in resource_data and resource_data['image']:
                # Si es una ruta estática (empieza con img/), usar static_image_path
                if str(resource_data['image']).startswith('img/'):
                    defaults['static_image_path'] = resource_data['image']
                else:
                    defaults['image'] = resource_data['image']

            resource_type, created = ResourceType.objects.get_or_create(
                name=resource_data['name'],
                defaults=defaults
            )
            if created:
                self.stdout.write(f'Created resource type: {resource_type.name}')

        # Load Building Types
        self.stdout.write('Loading building types...')
        for building_data in data.get('building_types', []):
            # Remove any legacy 'pk'
            building_data.pop('pk', None)
            defaults = {'name': building_data['name']}
            # Support static image filenames from JSON (e.g., img/campamento_principal.png)
            if 'image' in building_data and building_data['image']:
                # Si es una ruta estática (empieza con img/), usar static_image_path
                if str(building_data['image']).startswith('img/'):
                    defaults['static_image_path'] = building_data['image']
                else:
                    defaults['image'] = building_data['image']
            building_type, created = BuildingType.objects.get_or_create(
                type=building_data['type'],
                defaults=defaults
            )
            if created:
                self.stdout.write(f'Created building type: {building_type.name}')

        # Load Rarities
        self.stdout.write('Loading rarities...')
        for rarity_data in data.get('rarities', []):
            rarity_data.pop('pk', None)
            rarity, created = Rarity.objects.get_or_create(
                type=rarity_data['type']
            )
            if created:
                self.stdout.write(f'Created rarity: {rarity.type}')

        # Load Skills (new model)
        self.stdout.write('Loading skills...')
        for skill_data in data.get('abilities', []):  # backward compatibility: key named 'abilities'
            skill_data.pop('pk', None)
            skill, created = Skill.objects.get_or_create(
                name=skill_data['name'],
                defaults={
                    'description': skill_data.get('description', ''),
                    'effect_type': skill_data.get('effect_type', 'damage'),
                    'target': skill_data.get('target', 'enemy_single'),
                    'damage_profile': skill_data.get('damage_profile', 'physical'),
                    'scaling_stat': skill_data.get('scaling_stat', 'none'),
                    'base_value': skill_data.get('base_value', 0.0),
                    'percent_value': skill_data.get('percent_value', 0.0),
                    'passive_trigger': skill_data.get('passive_trigger', 'always'),
                    'rage_gain': skill_data.get('rage_gain', 0),
                    'rage_cost': skill_data.get('rage_cost', 0),
                    'per_level_multiplier': skill_data.get('per_level_multiplier', 0.0),
                    'max_level': skill_data.get('max_level', 1),
                }
            )
            if created:
                self.stdout.write(f'Created skill: {skill.name}')

        # Load Heroes
        self.stdout.write('Loading heroes...')
        for hero_data in data.get('heroes', []):
            hero_data.pop('pk', None)
            if not Hero.objects.filter(name=hero_data['name']).exists():
                rarity = Rarity.objects.get(type=hero_data['rarity'])
                # Map possible fields (new model may use atk/def split, etc.)
                extra = {}
                for k in ['image', 'codename', 'race', 'klass', 'primary_mechanic', 'damage_profile', 'subrole',
                          'base_hp', 'base_atk_mag', 'base_atk_phy', 'base_def_mag', 'base_def_phy', 'base_speed',
                          'base_crit_chance']:
                    if k in hero_data:
                        if k == 'image' and hero_data[k] and str(hero_data[k]).startswith('img/'):
                            # Si es una ruta estática, usar static_image_path
                            extra['static_image_path'] = hero_data[k]
                        else:
                            extra[k] = hero_data[k]
                # Backward fallback
                if 'base_attack' in hero_data and 'base_atk_mag' not in extra and 'base_atk_phy' not in extra:
                    extra['base_atk_mag'] = hero_data['base_attack']
                if 'base_defense' in hero_data and 'base_def_mag' not in extra and 'base_def_phy' not in extra:
                    extra['base_def_mag'] = hero_data['base_defense']
                hero = Hero.objects.create(
                    name=hero_data['name'],
                    rarity=rarity,
                    description=hero_data.get('description', ''),
                    **extra
                )
                # Add abilities to hero
                # Attach up to 4 skills to the hero in fixed slots (BASIC, ULTIMATE, PASSIVE_1, PASSIVE_2)
                slots_order = [SkillSlot.BASIC, SkillSlot.ULTIMATE, SkillSlot.PASSIVE_1, SkillSlot.PASSIVE_2]
                for idx, skill_name in enumerate(hero_data.get('abilities', [])):
                    if idx >= len(slots_order):
                        break
                    try:
                        skill = Skill.objects.get(name=skill_name)
                        HeroSkill.objects.get_or_create(hero=hero, skill=skill, slot=slots_order[idx])
                    except Skill.DoesNotExist:
                        self.stdout.write(f'⚠️  Skill not found: {skill_name}')
                self.stdout.write(f'Created hero: {hero.name}')

        # Load Enemies
        self.stdout.write('Loading enemies...')
        for enemy_data in data.get('enemies', []):
            enemy_data.pop('pk', None)

            # Process image path for static files
            defaults = {
                'base_hp': enemy_data['base_hp'],
                'attack': enemy_data['attack'],
                'defense': enemy_data['defense'],
                'speed': enemy_data['speed'],
                'description': enemy_data.get('description', '')
            }

            if 'image' in enemy_data and enemy_data['image']:
                # Si es una ruta estática (empieza con img/), usar static_image_path
                if str(enemy_data['image']).startswith('img/'):
                    defaults['static_image_path'] = enemy_data['image']
                else:
                    defaults['image'] = enemy_data['image']

            enemy, created = Enemy.objects.get_or_create(
                name=enemy_data['name'],
                defaults=defaults
            )
            if created:
                self.stdout.write(f'Created enemy: {enemy.name}')

        # Load Raids
        self.stdout.write('Loading raids...')
        for raid_data in data.get('raids', []):
            raid_data.pop('pk', None)
            raid, created = Raid.objects.get_or_create(
                name=raid_data['name'],
                defaults={
                    'description': raid_data.get('description', ''),
                    'difficulty': raid_data.get('difficulty', 'normal'),
                    'min_players': raid_data.get('min_players', 1),
                    'max_players': raid_data.get('max_players', 4),
                }
            )
            if created:
                self.stdout.write(f'Created raid: {raid.name}')

        # Load Raid Waves
        self.stdout.write('Loading raid waves...')
        for wave_data in data.get('raid_waves', []):
            raid = Raid.objects.get(name=wave_data['raid'])
            wave, created = RaidWave.objects.get_or_create(
                raid=raid,
                wave_number=wave_data['wave_number'],
                defaults={
                    'name': wave_data.get('name', f'Oleada {wave_data["wave_number"]}')
                }
            )
            if created:
                self.stdout.write(f'Created wave: {wave.raid.name} - {wave.name}')

        # Load Raid Enemies
        self.stdout.write('Loading raid enemies...')
        for enemy_data in data.get('raid_enemies', []):
            wave_info = enemy_data['wave']
            raid = Raid.objects.get(name=wave_info['raid'])
            wave = RaidWave.objects.get(raid=raid, wave_number=wave_info['wave_number'])
            enemy = Enemy.objects.get(name=enemy_data['enemy'])

            raid_enemy, created = RaidEnemy.objects.get_or_create(
                wave=wave,
                enemy=enemy,
                defaults={
                    'quantity': enemy_data.get('quantity', 1),
                    'level_modifier': enemy_data.get('level_modifier', 1.0)
                }
            )
            if created:
                self.stdout.write(f'Created raid enemy: {wave} - {enemy_data["quantity"]}x {enemy.name}')

        # Load Test Users
        self.stdout.write('Loading test users...')
        for user_data in data.get('test_users', []):
            user_data.pop('pk', None)
            # Check if member already exists by phone or email
            existing_member = Member.objects.filter(
                models.Q(phone=user_data['phone']) | models.Q(email=user_data['email'])
            ).first()

            if existing_member:
                self.stdout.write(f'Member already exists: {existing_member.name} (phone: {existing_member.phone})')
                # Non-destructive: keep existing member data unchanged
                member = existing_member
            else:
                # Create new member
                try:
                    member = Member.objects.create(
                        name=user_data['name'],
                        firstname=user_data['firstname'],
                        email=user_data['email'],
                        phone=user_data['phone'],
                        password_member=user_data['password']
                    )
                    self.stdout.write(f'Created new member: {member.name}')

                    # Create default buildings for new member
                    try:
                        member.create_default_buildings()
                        self.stdout.write(f'Created default buildings for: {member.name}')
                    except Exception as e:
                        self.stdout.write(f'Warning: Could not create buildings for {member.name}: {e}')

                except Exception as e:
                    self.stdout.write(f'Error creating member {user_data["name"]}: {e}')
                    continue

            # Add resources to user (non-destructive): only create if missing
            try:
                for resource_name, amount in user_data['resources'].items():
                    resource_type = ResourceType.objects.get(name=resource_name)
                    PlayerResource.objects.get_or_create(
                        member=member,
                        resource_type=resource_type,
                        defaults={'amount': amount}
                    )
            except Exception as e:
                self.stdout.write(f'Error adding resources to {member.name}: {e}')

            # Add heroes to user (non-destructive): only create if missing
            try:
                for hero_name in user_data['heroes']:
                    hero = Hero.objects.get(name=hero_name)
                    PlayerHero.objects.get_or_create(
                        member=member,
                        hero=hero,
                        defaults={'level': 1, 'experience': 0}
                    )
            except Exception as e:
                self.stdout.write(f'Error adding heroes to {member.name}: {e}')

        # Load Building Costs
        self.stdout.write('Loading building costs...')
        for cost_data in data.get('building_costs', []):
            building_type = BuildingType.objects.get(type=cost_data['building_type'])
            
            for cost in cost_data['costs']:
                resource_type = ResourceType.objects.get(name=cost['resource'])
                building_cost, created = BuildingLevelCost.objects.get_or_create(
                    building_type=building_type,
                    level=cost_data['level'],
                    resource_type=resource_type,
                    defaults={'amount': cost['amount']}
                )
                if created:
                    self.stdout.write(
                        f'Created building cost: {building_type.name} level {cost_data["level"]} - {resource_type.name}: {cost["amount"]}'
                    )

        self.stdout.write(
            self.style.SUCCESS('Successfully loaded all initial data!')
        )
