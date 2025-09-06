from django import template
from django.templatetags.static import static
from django.conf import settings

register = template.Library()

@register.filter
def game_image_url(image_field):
    """
    Get the correct URL for game images, handling both static and media files.
    In production (Vercel), media files are ephemeral, so we use static files.
    """
    if not image_field:
        return None
    
    # Convert to string to check the path
    image_path = str(image_field)
    
    # If it's already a static path (starts with img/), use static
    if image_path.startswith('img/'):
        return static(image_path)
    
    # Otherwise, use the media URL (for local development or actual uploads)
    return image_field.url

@register.simple_tag
def game_asset_url(asset_path):
    """
    Get URL for a game asset from static files.
    Usage: {% game_asset_url 'img/hero_placeholder.png' %}
    """
    return static(asset_path)
