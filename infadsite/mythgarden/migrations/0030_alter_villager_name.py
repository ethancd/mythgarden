# Generated by Django 4.1.5 on 2023-02-07 21:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mythgarden', '0029_villagerstate_has_ever_been_talked_to_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='villager',
            name='name',
            field=models.CharField(max_length=255, unique=True),
        ),
    ]
