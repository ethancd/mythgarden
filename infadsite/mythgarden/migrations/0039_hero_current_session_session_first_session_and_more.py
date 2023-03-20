# Generated by Django 4.1.5 on 2023-03-15 21:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mythgarden', '0038_hero_remove_herostate_image_path_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='hero',
            name='current_session',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='mythgarden.session'),
        ),
        migrations.AddField(
            model_name='session',
            name='first_session',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='herostate',
            name='hero',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mythgarden.hero', null=True),
        ),
    ]
