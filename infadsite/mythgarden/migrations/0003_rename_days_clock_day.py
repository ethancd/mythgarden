# Generated by Django 4.1.5 on 2023-01-19 17:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mythgarden', '0002_alter_rucksack_contents_alter_situation_contents_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='clock',
            old_name='days',
            new_name='day',
        ),
    ]