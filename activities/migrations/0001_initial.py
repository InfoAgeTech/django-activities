# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Activity',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('created_dttm', models.DateTimeField(default=datetime.datetime.utcnow)),
                ('last_modified_dttm', models.DateTimeField(default=datetime.datetime.utcnow)),
                ('text', models.TextField(blank=True, null=True)),
                ('about_id', models.PositiveIntegerField(blank=True, null=True)),
                ('source', models.CharField(max_length=20, choices=[('SYSTEM', 'System'), ('USER', 'User')])),
                ('action', models.CharField(max_length=20, choices=[('COMMENTED', 'Commented'), ('CREATED', 'Created'), ('DELETED', 'Deleted'), ('UPDATED', 'Updated')])),
                ('privacy', models.CharField(max_length=20, choices=[('PUBLIC', 'Public - everyone can see'), ('PRIVATE', 'Private - only created user can see'), ('CUSTOM', 'Custom - users must be granted visibility')], default='PUBLIC')),
                ('about_content_type', models.ForeignKey(to='contenttypes.ContentType', null=True, blank=True)),
                ('created_user', models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='activities_activity_created_user+')),
            ],
            options={
                'ordering': ('-id',),
            },
        ),
        migrations.CreateModel(
            name='ActivityFor',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('object_id', models.PositiveIntegerField(db_index=True)),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ActivityReply',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('created_dttm', models.DateTimeField(default=datetime.datetime.utcnow)),
                ('last_modified_dttm', models.DateTimeField(default=datetime.datetime.utcnow)),
                ('text', models.TextField(max_length=500)),
                ('activity', models.ForeignKey(to='activities.Activity')),
                ('created_user', models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='activities_activityreply_created_user+')),
                ('last_modified_user', models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='activities_activityreply_last_modified_user+')),
                ('reply_to', models.ForeignKey(to='activities.ActivityReply', null=True, blank=True)),
            ],
            options={
                'ordering': ('id',),
            },
        ),
        migrations.AddField(
            model_name='activity',
            name='for_objs',
            field=models.ManyToManyField(to='activities.ActivityFor', blank=True, related_name='for_objs'),
        ),
        migrations.AddField(
            model_name='activity',
            name='last_modified_user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='activities_activity_last_modified_user+'),
        ),
        migrations.AddField(
            model_name='activity',
            name='replies',
            field=models.ManyToManyField(to='activities.ActivityReply', blank=True, related_name='replies'),
        ),
        migrations.AlterIndexTogether(
            name='activity',
            index_together=set([('about_content_type', 'about_id')]),
        ),
    ]
