# Generated by Django 4.1.5 on 2023-01-19 17:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mythgarden', '0004_alter_clock_day'),
    ]

    operations = [
        migrations.AlterField(
            model_name='clock',
            name='day',
            field=models.IntegerField(choices=[(0, 'Sun'), (1, 'Mon'), (2, 'Tue'), (3, 'Wed'), (4, 'Thu'), (5, 'Fri'), (6, 'Sat')]),
        ),
    ]