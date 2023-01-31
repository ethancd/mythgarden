# Generated by Django 4.1.5 on 2023-01-31 18:39

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mythgarden', '0006_villager_full_name_alter_place_name_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='villager',
            name='friendliness',
            field=models.IntegerField(default=4, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(7)]),
        ),
    ]
