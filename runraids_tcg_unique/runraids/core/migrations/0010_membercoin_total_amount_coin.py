# Generated by Django 5.1.1 on 2025-04-07 10:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_booster_cost_coin_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='membercoin',
            name='total_amount_coin',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
