# Generated by Django 4.1.5 on 2023-01-19 16:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mythgarden', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rucksack',
            name='contents',
            field=models.ManyToManyField(blank=True, to='mythgarden.item'),
        ),
        migrations.AlterField(
            model_name='situation',
            name='contents',
            field=models.ManyToManyField(blank=True, to='mythgarden.item'),
        ),
        migrations.AlterField(
            model_name='situation',
            name='occupants',
            field=models.ManyToManyField(blank=True, to='mythgarden.villager'),
        ),
    ]