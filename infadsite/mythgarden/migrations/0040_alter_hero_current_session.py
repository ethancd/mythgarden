# Generated by Django 4.1.5 on 2023-03-15 21:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mythgarden', '0039_hero_current_session_session_first_session_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='hero',
            name='current_session',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='mythgarden.session', unique=True),
        ),
    ]