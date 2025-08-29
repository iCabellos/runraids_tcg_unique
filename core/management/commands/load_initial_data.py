import json
import os
from django.core.management.base import BaseCommand
from django.conf import settings

# Try to import models, handle gracefully if not available
try:
    from core.models import (
        ResourceType, BuildingType, Rarity, Ability, Hero, Enemy, Member,
        PlayerResource, PlayerHero, BuildingLevelCost, PlayerBuilding
    )
    models_available = True
except ImportError as e:
    models_available = False
    import_error = str(e)


class Command(BaseCommand):
    help = 'Load initial data from JSON file'

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
                type=rarity_data['type'],
                defaults={'multiplier': rarity_data['multiplier']}
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
                    'hp': enemy_data['hp'],
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
            if not Member.objects.filter(phone=user_data['phone']).exists():
                member = Member.objects.create(
                    name=user_data['name'],
                    firstname=user_data['firstname'],
                    email=user_data['email'],
                    phone=user_data['phone'],
                    password_member=user_data['password']  # Will be hashed automatically
                )
                
                # Add resources to user
                for resource_name, amount in user_data['resources'].items():
                    resource_type = ResourceType.objects.get(name=resource_name)
                    PlayerResource.objects.create(
                        member=member,
                        resource_type=resource_type,
                        amount=amount
                    )
                
                # Add heroes to user
                for hero_name in user_data['heroes']:
                    hero = Hero.objects.get(name=hero_name)
                    PlayerHero.objects.create(
                        member=member,
                        hero=hero,
                        level=1,
                        experience=0
                    )
                
                self.stdout.write(f'Created test user: {member.name}')

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
