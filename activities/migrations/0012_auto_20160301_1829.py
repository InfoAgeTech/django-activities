# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-03-01 18:29
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('activities', '0011_activity_group'),
    ]

    operations = [
        migrations.AlterField(
            model_name='activity',
            name='group',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='grouping', to='activities.Activity'),
        ),
    ]
