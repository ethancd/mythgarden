# Generated by Django 4.1.5 on 2023-01-31 19:02

from django.db import migrations, models
import django.db.models.deletion
import mythgarden.models


class Migration(migrations.Migration):

    dependencies = [
        ('mythgarden', '0007_villager_friendliness'),
    ]

    operations = [
        migrations.AlterField(
            model_name='action',
            name='cost_unit',
            field=models.CharField(choices=[('MINUTE', 'min'), ('HOUR', 'hour'), ('DAY', 'day'), ('KOIN', '₭')], max_length=6),
        ),
        migrations.AlterField(
            model_name='session',
            name='location',
            field=models.ForeignKey(default=mythgarden.models.place.Place.get_default_pk, null=True, on_delete=django.db.models.deletion.CASCADE, to='mythgarden.place'),
        ),
    ]
