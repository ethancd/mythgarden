# Generated by Django 4.1.5 on 2023-04-07 05:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mythgarden', '0057_building_down_building_over_alter_action_action_type_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='action',
            name='cost_wait_class',
            field=models.CharField(blank=True, choices=[('TRIVIAL', 'trivial'), ('TRIVIAL_PLUS', 'trivialPlus'), ('SMALL_MINUS', 'smallMinus'), ('SMALL', 'small'), ('SMALL_PLUS', 'smallPlus'), ('MEDIUM_MINUS', 'mediumMinus'), ('MEDIUM', 'medium'), ('MEDIUM_PLUS', 'mediumPlus'), ('LONG_MINUS', 'longMinus'), ('LONG', 'long')], max_length=12, null=True),
        ),
        migrations.AlterField(
            model_name='action',
            name='cost_amount',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
