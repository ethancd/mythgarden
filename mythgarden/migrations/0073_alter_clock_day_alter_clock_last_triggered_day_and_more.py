# Generated by Django 4.1.5 on 2023-04-22 17:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mythgarden', '0072_mythlingstate_is_in_possession'),
    ]

    operations = [
        migrations.AlterField(
            model_name='clock',
            name='day',
            field=models.CharField(choices=[('MON', 'Monday'), ('TUE', 'Tuesday'), ('WED', 'Wednesday'), ('THU', 'Thursday'), ('FRI', 'Friday'), ('SAT', 'Saturday'), ('SUN', 'Sunday')], default='MON', max_length=9),
        ),
        migrations.AlterField(
            model_name='clock',
            name='last_triggered_day',
            field=models.CharField(choices=[('MON', 'Monday'), ('TUE', 'Tuesday'), ('WED', 'Wednesday'), ('THU', 'Thursday'), ('FRI', 'Friday'), ('SAT', 'Saturday'), ('SUN', 'Sunday')], default='MON', max_length=9),
        ),
        migrations.AlterField(
            model_name='scheduledevent',
            name='day',
            field=models.CharField(blank=True, choices=[('MON', 'Monday'), ('TUE', 'Tuesday'), ('WED', 'Wednesday'), ('THU', 'Thursday'), ('FRI', 'Friday'), ('SAT', 'Saturday'), ('SUN', 'Sunday')], max_length=9, null=True),
        ),
    ]