# Generated by Django 4.1.5 on 2023-01-19 22:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('mythgarden', '0009_alter_action_action_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='action',
            name='secondary_content_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='secondary_content_type', to='contenttypes.contenttype'),
        ),
        migrations.AddField(
            model_name='action',
            name='secondary_object_id',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='action',
            name='content_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='contenttypes.contenttype'),
        ),
        migrations.AlterField(
            model_name='action',
            name='object_id',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
    ]
