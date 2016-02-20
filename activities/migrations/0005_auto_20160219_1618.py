# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-02-19 16:18
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('activities', '0004_auto_20160219_0532'),
    ]

    operations = [
        migrations.AlterIndexTogether(
            name='activity',
            index_together=set([('created_user', 'action', 'privacy', 'id'), ('about_id', 'about_content_type', 'id')]),
        ),
    ]
