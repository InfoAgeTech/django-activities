# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.contenttypes.models import ContentType

class NotificationManager(models.Manager):

# Don't think I need this because the "get_for_object" covers the case of getting
# all notifications for an object.
#    def get_about_object(self, obj):
#        """Gets the notifications about this object."""
#        content_type = ContentType.objects.get_for_model(obj)
#        return self.filter(about_content_type=content_type, about_id=obj.id)

    def get_for_object(self, obj):
        """Gets all notifications relating to this specific object.
        
        :param obj: get all notifications for this object.
        """
        content_type = ContentType.objects.get_for_model(obj)
        return self.filter(for_objs__content_type=content_type,
                           for_objs__object_id=obj.id)
