# Generated by Django 4.1.5 on 2023-01-08 22:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('adventure', '0004_remove_quandary_parent_answer_answer_child_quandary'),
    ]

    operations = [
        migrations.AlterField(
            model_name='answer',
            name='child_quandary',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='parent_answer', to='adventure.quandary'),
        ),
        migrations.AlterField(
            model_name='hero',
            name='portrait',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='heroes', to='adventure.portrait'),
        ),
        migrations.AlterField(
            model_name='quandary',
            name='landscape',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='adventure.landscape'),
        ),
    ]
