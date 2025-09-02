# core/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Member, Hero, PlayerHero

DEFAULT_HERO_CODENAME = "novato"

@receiver(post_save, sender=Member)
def give_default_hero(sender, instance: Member, created: bool, **kwargs):
    if not created:
        return
    try:
        hero = Hero.objects.get(codename=DEFAULT_HERO_CODENAME)
    except Hero.DoesNotExist:
        return  # opcional: loggear un warning
    PlayerHero.objects.get_or_create(member=instance, hero=hero, defaults={"experience": 0})
