# Generated by Django 4.0.5 on 2022-11-22 11:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0025_coois_planning_pproval_zpp_planning_pproval'),
    ]

    operations = [
        migrations.RenameField(
            model_name='coois',
            old_name='planning_pproval',
            new_name='planning_approval',
        ),
        migrations.RenameField(
            model_name='zpp',
            old_name='planning_pproval',
            new_name='planning_approval',
        ),
    ]
