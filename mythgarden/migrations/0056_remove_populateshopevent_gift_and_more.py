# Generated by Django 4.1.5 on 2023-04-01 05:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mythgarden', '0055_alter_villager_home'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='populateshopevent',
            name='gift',
        ),
        migrations.RemoveField(
            model_name='populateshopevent',
            name='gift_quantity',
        ),
        migrations.RemoveField(
            model_name='populateshopevent',
            name='merch_slots',
        ),
        migrations.RemoveField(
            model_name='populateshopevent',
            name='seed',
        ),
        migrations.AddField(
            model_name='populateshopevent',
            name='content_config_list',
            field=models.JSONField(default=list),
        ),
        migrations.AlterField(
            model_name='action',
            name='cost_unit',
            field=models.CharField(blank=True, choices=[('MINUTE', '🕒'), ('HOUR', 'hr'), ('KOIN', '⚜️')], max_length=6, null=True),
        ),
        migrations.AlterField(
            model_name='item',
            name='item_type',
            field=models.CharField(choices=[('SEED', 'Seed'), ('SPROUT', 'Sprout'), ('CROP', 'Crop'), ('GIFT', 'Gift'), ('FISH', 'Fish'), ('MINERAL', 'Mineral'), ('FOSSIL', 'Fossil'), ('TECH', 'Tech'), ('MAGIC', 'Magic'), ('HERB', 'Herb'), ('FLOWER', 'Flower'), ('BERRY', 'Berry')], default='GIFT', max_length=8),
        ),
        migrations.AlterField(
            model_name='itemtypepreference',
            name='item_type',
            field=models.CharField(choices=[('SEED', 'Seed'), ('SPROUT', 'Sprout'), ('CROP', 'Crop'), ('GIFT', 'Gift'), ('FISH', 'Fish'), ('MINERAL', 'Mineral'), ('FOSSIL', 'Fossil'), ('TECH', 'Tech'), ('MAGIC', 'Magic'), ('HERB', 'Herb'), ('FLOWER', 'Flower'), ('BERRY', 'Berry')], max_length=8),
        ),
        migrations.AlterField(
            model_name='merchslot',
            name='merch_slot_type',
            field=models.CharField(choices=[('MINOR', 'minor'), ('MEDIUM', 'medium'), ('MAJOR', 'major'), ('GRAND', 'grand'), ('SUPREME', 'supreme')], max_length=7),
        ),
    ]