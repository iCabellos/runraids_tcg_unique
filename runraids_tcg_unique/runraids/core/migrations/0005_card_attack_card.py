# Generated by Django 5.1.6 on 2025-02-23 11:48

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_card_ability_card_hero_ability_hero_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='card',
            name='attack_card',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='core.attack'),
        ),
    ]
