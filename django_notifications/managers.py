# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.contenttypes.models import ContentType


class NotificationManager(models.Manager):

    def get_by_user(self, user, **kwargs):
        """Gets notifications for a user.

        :param user: the user to get the notifications for

        """
        return self.get_by_obj(obj=user, **kwargs)

    def get_by_obj(self, obj, **kwargs):
        """Gets notifications for a specific object.
        
        :param obj: the object the notifications are for
        :param kwargs: any key value pair fields that are on the model.
        
        """
        content_type = ContentType.objects.get_for_model(obj)
        return self.filter(for_objs__content_type=content_type,
                           for_objs__object_id=obj.id,
                           **kwargs)


class NotificationForManager(models.Manager):

    def get_or_create_generic(self, obj, **kwargs):
        """Gets or creates a generic object.  This is a wrapper for 
        get_or_create(...) when you need to get or create a generic object.
        
        :param obj: the object to get or create
        :param kwargs: any other kwargs that the model accepts.
        """
        content_type = ContentType.objects.get_for_model(obj)
        return self.get_or_create(content_type=content_type,
                                  object_id=obj.id,
                                  **kwargs)

    def get_by_content_type(self, content_type):
        """Gets all objects by a content type."""
        return self.filter(content_type=content_type)

    def get_by_model(self, model):
        """Gets all object by a specific model."""
        content_type = ContentType.objects.get_for_model(model)
        return self.filter(content_type=content_type)


class NotificationReplyManager(models.Manager):

    def get_by_notification(self, notification):
        """Gets all objects for a notification object."""
        try:
            return self.get(notification=notification)
        except self.model.DoesNotExist:
            return None

    def get_by_notification_id(self, notification_id):
        """Gets all objects by notification id."""
        try:
            return self.get(notification_id=notification_id)
        except self.model.DoesNotExist:
            return None

