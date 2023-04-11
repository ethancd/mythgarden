# Generated by Django 4.1.5 on 2023-04-11 23:04

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mythgarden', '0062_clock_last_triggered_day_clock_last_triggered_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='clock',
            name='last_triggered_day',
            field=models.CharField(choices=[('MON', 'Mon'), ('TUE', 'Tue'), ('WED', 'Wed'), ('THU', 'Thu'), ('FRI', 'Fri'), ('SAT', 'Sat'), ('SUN', 'Sun')], default='MON', max_length=9),
        ),
        migrations.AlterField(
            model_name='clock',
            name='last_triggered_time',
            field=models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1439)]),
        ),
    ]
