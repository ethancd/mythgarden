# Generated by Django 4.1.5 on 2023-01-26 19:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mythgarden', '0014_alter_clock_time'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Rucksack',
            new_name='Inventory',
        ),
        migrations.AlterField(
            model_name='clock',
            name='day',
            field=models.CharField(choices=[('SUN', 'Sun'), ('MON', 'Mon'), ('TUE', 'Tue'), ('WED', 'Wed'), ('THU', 'Thu'), ('FRI', 'Fri'), ('SAT', 'Sat')], default='SUN', max_length=9),
        ),
    ]
