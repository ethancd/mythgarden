# Generated by Django 4.1.5 on 2023-03-25 23:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mythgarden', '0050_alter_villagerstate_location'),
    ]

    operations = [
        migrations.AlterField(
            model_name='villagerstate',
            name='location',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='villagers', to='mythgarden.place'),
        ),
    ]
