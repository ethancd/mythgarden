# Generated by Django 4.1.5 on 2023-03-29 21:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mythgarden', '0054_place_has_inventory_alter_action_action_type_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='villager',
            name='home',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='residents', to='mythgarden.building'),
        ),
    ]