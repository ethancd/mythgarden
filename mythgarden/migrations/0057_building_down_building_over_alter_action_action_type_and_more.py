# Generated by Django 4.1.5 on 2023-04-04 23:30

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mythgarden', '0056_remove_populateshopevent_gift_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='building',
            name='down',
            field=models.IntegerField(default=2, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(3)]),
        ),
        migrations.AddField(
            model_name='building',
            name='over',
            field=models.IntegerField(default=2, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(3)]),
        ),
        migrations.AlterField(
            model_name='action',
            name='action_type',
            field=models.CharField(choices=[('TRAVEL', 'Travel'), ('TALK', 'Talk'), ('GIVE', 'Give'), ('PLANT', 'Plant'), ('WATER', 'Water'), ('HARVEST', 'Harvest'), ('BUY', 'Buy'), ('SELL', 'Sell'), ('STOW', 'Stow'), ('RETRIEVE', 'Retrieve'), ('GATHER', 'Gather'), ('SLEEP', 'Sleep')], max_length=8),
        ),
        migrations.AlterField(
            model_name='bridge',
            name='place_1',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bridges_as_1', to='mythgarden.place'),
        ),
        migrations.AlterField(
            model_name='bridge',
            name='place_2',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bridges_as_2', to='mythgarden.place'),
        ),
    ]
