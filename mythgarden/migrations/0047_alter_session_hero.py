# Generated by Django 4.1.5 on 2023-03-20 16:23

from django.db import migrations, models
import django.db.models.deletion
import mythgarden.models.hero


class Migration(migrations.Migration):

    dependencies = [
        ('mythgarden', '0046_alter_herostate_hero_alter_session_hero'),
    ]

    operations = [
        migrations.AlterField(
            model_name='session',
            name='hero',
            field=models.ForeignKey(default=mythgarden.models.hero.Hero.get_default_pk, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='current_session', to='mythgarden.hero'),
        ),
    ]
