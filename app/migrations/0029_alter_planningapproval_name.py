# Generated by Django 4.0.5 on 2022-11-24 11:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0028_alter_planningapproval_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='planningapproval',
            name='name',
            field=models.CharField(max_length=200),
        ),
    ]