# Generated by Django 5.1.1 on 2025-04-02 10:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_booster_set_booster'),
    ]

    operations = [
        migrations.AddField(
            model_name='booster',
            name='quantity_of_cards',
            field=models.IntegerField(default=1),
        ),
    ]
