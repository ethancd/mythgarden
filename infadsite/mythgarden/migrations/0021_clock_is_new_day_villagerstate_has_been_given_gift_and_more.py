# Generated by Django 4.1.5 on 2023-02-05 22:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mythgarden', '0020_alter_action_cost_unit'),
    ]

    operations = [
        migrations.AddField(
            model_name='clock',
            name='is_new_day',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='villagerstate',
            name='has_been_given_gift',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='villagerstate',
            name='has_been_greeted',
            field=models.BooleanField(default=False),
        ),
        migrations.CreateModel(
            name='ItemState',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('has_been_watered', models.BooleanField(default=False)),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='states', to='mythgarden.item')),
                ('session', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='item_states', to='mythgarden.session')),
            ],
        ),
    ]
