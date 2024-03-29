# Generated by Django 4.1.5 on 2023-04-12 19:30

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mythgarden', '0066_rename_location_session__location'),
    ]

    operations = [
        migrations.RenameField(
            model_name='villagerstate',
            old_name='has_ever_been_talked_to',
            new_name='has_ever_been_interacted_with',
        ),
        migrations.AddField(
            model_name='herostate',
            name='farming_intake',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='herostate',
            name='farming_koin_earned',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='herostate',
            name='fishing_intake',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='herostate',
            name='fishing_koin_earned',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='herostate',
            name='foraging_intake',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='herostate',
            name='foraging_koin_earned',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='herostate',
            name='mining_intake',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='herostate',
            name='mining_koin_earned',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='villagerstate',
            name='talked_to_count',
            field=models.IntegerField(default=0),
        ),
        migrations.CreateModel(
            name='Achievement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('description', models.CharField(max_length=255)),
                ('achievement_type', models.CharField(choices=[('ALL_VILLAGERS_HEARTS', 'All villagers hearts'), ('MULTIPLE_BEST_FRIENDS', 'Multiple best friends'), ('BEST_FRIENDS', 'Best friends'), ('FAST_FRIENDS', 'Fast friends'), ('STEADFAST_FRIENDS', 'Steadfast friends'), ('BESTEST_FRIENDS', 'Bestest friends'), ('FASTEST_FRIENDS', 'Fastest friends'), ('STEADFASTEST_FRIENDS', 'Steadfastest friends'), ('GROSS_INCOME', 'Gross income'), ('BALANCED_INCOME', 'Balanced income'), ('FARMING_INTAKE', 'Farming intake'), ('MINING_INTAKE', 'Mining intake'), ('FISHING_INTAKE', 'Fishing intake'), ('FORAGING_INTAKE', 'Foraging intake'), ('FAST_CASH', 'Fast cash')], max_length=24)),
                ('trigger_type', models.CharField(choices=[('GAIN_HEARTS', 'Gain hearts'), ('TALK_TO_VILLAGERS', 'Talk to villagers'), ('GAIN_ACHIEVEMENT', 'Gain achievement'), ('EARN_MONEY', 'Earn money'), ('HARVEST', 'Harvest'), ('GATHER', 'Gather')], max_length=24)),
                ('threshold', models.IntegerField(blank=True, null=True)),
                ('threshold_day_number', models.IntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(6)])),
                ('villager', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='mythgarden.villager')),
            ],
        ),
        migrations.AddField(
            model_name='hero',
            name='achievements',
            field=models.ManyToManyField(blank=True, to='mythgarden.achievement'),
        ),
    ]
