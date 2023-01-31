# Generated by Django 4.1.5 on 2023-01-31 18:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mythgarden', '0005_remove_building_building_type_remove_place_land_type_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='villager',
            name='full_name',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='place',
            name='name',
            field=models.CharField(max_length=255, unique=True),
        ),
        migrations.AlterField(
            model_name='villager',
            name='portrait',
            field=models.ImageField(blank=True, default='portraits/squall-farmer.png', null=True, upload_to='portraits/'),
        ),
    ]
