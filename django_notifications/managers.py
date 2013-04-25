# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.contenttypes.models import ContentType

class NotificationManager(models.Manager):

    def get_about_object(self, obj):
        """Gets the notifications about this object."""
        content_type = ContentType.objects.get_for_model(obj)
        return self.filter(about_content_type=content_type, about_id=obj.id)
