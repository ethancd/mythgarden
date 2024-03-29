# Generated by Django 4.1.5 on 2023-03-16 18:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mythgarden', '0042_alter_hero_current_session_alter_herostate_session'),
    ]

    operations = [
        migrations.RenameField(
            model_name='session',
            old_name='first_session',
            new_name='is_first_session',
        ),
        migrations.RemoveField(
            model_name='hero',
            name='current_session',
        ),
        migrations.AddField(
            model_name='session',
            name='hero',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='current_session', to='mythgarden.hero'),
        ),
    ]
