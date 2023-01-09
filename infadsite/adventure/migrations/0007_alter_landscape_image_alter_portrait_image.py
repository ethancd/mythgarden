# Generated by Django 4.1.5 on 2023-01-08 23:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adventure', '0006_remove_quandary_landscape_landscape_quandary'),
    ]

    operations = [
        migrations.AlterField(
            model_name='landscape',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='static/adventure/images/landscapes/'),
        ),
        migrations.AlterField(
            model_name='portrait',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='static/adventure/images/portraits/'),
        ),
    ]
