import json
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from django.db import models

# Try to import models, handle gracefully if not available
try:
    from core.models import (
        ResourceType, BuildingType, Rarity, Ability, Hero, Enemy, Member,
        PlayerResource, PlayerHero, BuildingLevelCost, PlayerBuilding
    )
    from django.contrib.auth.models import User

    models_available = True
except ImportError as e:
    models_available = False
    import_error = str(e)


class Command(BaseCommand):
    help = 'Load initial data from JSON file'

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

        # Path to the JSON file
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
                Ability.objects.all().delete()
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
                # Update existing user
                user.email = admin_data['email']
                user.first_name = admin_data.get('first_name', '')
                user.last_name = admin_data.get('last_name', '')
                user.is_superuser = admin_data.get('is_superuser', False)
                user.is_staff = admin_data.get('is_staff', False)
                user.set_password(admin_data['password'])
                user.save()
                self.stdout.write(f'Updated Django admin user: {user.username}')

        # Load Resource Types
        self.stdout.write('Loading resource types...')
        for resource_data in data.get('resource_types', []):
            resource_type, created = ResourceType.objects.get_or_create(
                name=resource_data['name'],
                defaults={'description': resource_data['description']}
            )
            if created:
                self.stdout.write(f'Created resource type: {resource_type.name}')

        # Load Building Types
        self.stdout.write('Loading building types...')
        for building_data in data.get('building_types', []):
            building_type, created = BuildingType.objects.get_or_create(
                type=building_data['type'],
                defaults={'name': building_data['name']}
            )
            if created:
                self.stdout.write(f'Created building type: {building_type.name}')

        # Load Rarities
        self.stdout.write('Loading rarities...')
        for rarity_data in data.get('rarities', []):
            rarity, created = Rarity.objects.get_or_create(
                type=rarity_data['type']
            )
            if created:
                self.stdout.write(f'Created rarity: {rarity.type}')

        # Load Abilities
        self.stdout.write('Loading abilities...')
        for ability_data in data.get('abilities', []):
            ability, created = Ability.objects.get_or_create(
                name=ability_data['name'],
                defaults={
                    'type': ability_data['type'],
                    'power': ability_data['power'],
                    'description': ability_data['description']
                }
            )
            if created:
                self.stdout.write(f'Created ability: {ability.name}')

        # Load Heroes
        self.stdout.write('Loading heroes...')
        for hero_data in data.get('heroes', []):
            if not Hero.objects.filter(name=hero_data['name']).exists():
                rarity = Rarity.objects.get(type=hero_data['rarity'])
                hero = Hero.objects.create(
                    name=hero_data['name'],
                    rarity=rarity,
                    description=hero_data['description'],
                    base_hp=hero_data['base_hp'],
                    base_attack=hero_data['base_attack'],
                    base_defense=hero_data['base_defense'],
                    base_speed=hero_data['base_speed']
                )
                
                # Add abilities to hero
                for ability_name in hero_data['abilities']:
                    ability = Ability.objects.get(name=ability_name)
                    hero.abilities.add(ability)
                
                self.stdout.write(f'Created hero: {hero.name}')

        # Load Enemies
        self.stdout.write('Loading enemies...')
        for enemy_data in data.get('enemies', []):
            enemy, created = Enemy.objects.get_or_create(
                name=enemy_data['name'],
                defaults={
                    'base_hp': enemy_data['base_hp'],
                    'attack': enemy_data['attack'],
                    'defense': enemy_data['defense'],
                    'speed': enemy_data['speed'],
                    'description': enemy_data['description']
                }
            )
            if created:
                self.stdout.write(f'Created enemy: {enemy.name}')

        # Load Test Users
        self.stdout.write('Loading test users...')
        for user_data in data.get('test_users', []):
            # Check if member already exists by phone or email
            existing_member = Member.objects.filter(
                models.Q(phone=user_data['phone']) | models.Q(email=user_data['email'])
            ).first()

            if existing_member:
                self.stdout.write(f'Member already exists: {existing_member.name} (phone: {existing_member.phone})')
                # Update existing member instead of creating new one
                member = existing_member
                member.name = user_data['name']
                member.firstname = user_data['firstname']
                member.email = user_data['email']
                member.phone = user_data['phone']
                member.password_member = user_data['password']
                member.save()
                self.stdout.write(f'Updated existing member: {member.name}')

                # Clear existing resources and heroes to avoid duplicates
                PlayerResource.objects.filter(member=member).delete()
                PlayerHero.objects.filter(member=member).delete()
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

            # Add resources to user
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

            # Add heroes to user
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
