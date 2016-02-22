# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-02-18 22:51
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('activities', '0002_auto_20160125_1811'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='activity',
            options={},
        ),
        migrations.AlterField(
            model_name='activity',
            name='action',
            field=models.CharField(choices=[('ADDED', 'Added'), ('COMMENTED', 'Commented'), ('CREATED', 'Created'), ('DELETED', 'Deleted'), ('EDITED', 'Edited'), ('SHARED', 'Shared'), ('UPDATED', 'Updated'), ('UPLOADED', 'Uploaded')], max_length=20),
        ),
    ]