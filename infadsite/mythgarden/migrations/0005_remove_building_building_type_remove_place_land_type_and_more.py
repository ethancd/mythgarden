# Generated by Django 4.1.5 on 2023-01-27 23:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mythgarden', '0004_session_skip_post_save_signal'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='building',
            name='building_type',
        ),
        migrations.RemoveField(
            model_name='place',
            name='land_type',
        ),
        migrations.AddField(
            model_name='place',
            name='place_type',
            field=models.CharField(choices=[('FARM', 'Farm'), ('WILD', 'Wild'), ('TOWN', 'Town'), ('SHOP', 'Shop'), ('HOME', 'Home')], default='WILD', max_length=4),
        ),
    ]
