# Generated manually to update existing resource static image paths

from django.db import migrations

def update_resource_static_images(apps, schema_editor):
    """Update existing resources to use static image paths"""
    ResourceType = apps.get_model('core', 'ResourceType')
    
    # Mapping of resource names to static image paths
    resource_images = {
        'Oro': 'img/campamento_principal.png',
        'Madera': 'img/alijo_principal.png',
        'Elixir': 'img/hoguera.png',
    }
    
    for resource_name, image_path in resource_images.items():
        try:
            resource = ResourceType.objects.get(name=resource_name)
            resource.static_image_path = image_path
            resource.save()
            print(f'Updated {resource_name} with static_image_path: {image_path}')
        except ResourceType.DoesNotExist:
            print(f'Resource {resource_name} not found, skipping')

def reverse_update_resource_static_images(apps, schema_editor):
    """Reverse the update by clearing static_image_path"""
    ResourceType = apps.get_model('core', 'ResourceType')
    
    resource_names = ['Oro', 'Madera', 'Elixir']
    
    for resource_name in resource_names:
        try:
            resource = ResourceType.objects.get(name=resource_name)
            resource.static_image_path = None
            resource.save()
            print(f'Cleared static_image_path for {resource_name}')
        except ResourceType.DoesNotExist:
            print(f'Resource {resource_name} not found, skipping')

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_buildingtype_static_image_path_and_more'),
    ]

    operations = [
        migrations.RunPython(
            update_resource_static_images,
            reverse_update_resource_static_images,
        ),
    ]
