# Generated by Django 4.1.5 on 2023-04-12 00:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mythgarden', '0065_alter_session_location'),
    ]

    operations = [
        migrations.RenameField(
            model_name='session',
            old_name='location',
            new_name='_location',
        ),
    ]
