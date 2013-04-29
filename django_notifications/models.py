# -*- coding: utf-8 -*-
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django_notifications.constants import NotificationSource
from django_tools.models import AbstractBaseModel
from django_notifications.managers import NotificationManager
from django_notifications.managers import NotificationForManager
from django_notifications.managers import NotificationReplyManager


class NotificationReply(AbstractBaseModel):
    """Represents a notification reply object.
    
    Attributes:
    
    * text: the text of the notification.  This can include html.
    * created_id: the person the notification was from.  This is the user who
            caused the notification to change.  This can be the same user as the 
            notification is intended for (users can create notifications for 
            themselves)
    * reply_to_id: this is a reply to a reply and is the id of the reply.
      
    """
    text = models.TextField(max_length=500)
    notification = models.ForeignKey('Notification')
    reply_to_id = models.PositiveIntegerField(blank=True, null=True)
    objects = NotificationReplyManager()

    class Meta:
        ordering = ('-created_dttm',)


# TODO: Rename this to something like "NotificationRelations" since it includes the
# objects that are related to a notification.
class NotificationFor(models.Model):
    """Defines the generic object a notification is for.
    
    TODO: Should make this a mixin! Or,
    TODO: Is this it's own model that basically creates a ManyToMany Relationship
          to whatever is referencing the object?
          - then I could make this a proxy moxel...
    TODO: prove out performance works for this before making it a separate app (django-generic).
    """

    class Meta:
        db_table = u'notifications_for'

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    for_object = generic.GenericForeignKey('content_type', 'object_id')
    objects = NotificationForManager()


class Notification(AbstractBaseModel):
    """Notifications.
    
    Attributes: 
    
    * about: object the notification is referring to.
    * about_id: id this object the notification pertains to.
    * about_content_type: the content type of the about object
    * text: the text of the notification.  This can include html.
    * replies: list of replies to this notification
    * for_objs: list of docs this notification is for. For example,
        if a comment is made on a object "A" which has an object "B", then this
        list will include references to the::
            
            1. object "A"
            2. object "B" 
            4. users who are sharing this object
            
    * source: the source of notification.  Can be one if NotificationSource 
        choices (i.e. 'user' generated comment, 'activity' on a bill, etc)

    """

    text = models.TextField()
    about_content_type = models.ForeignKey(ContentType)
    about = generic.GenericForeignKey('about_content_type', 'about_id')
    about_id = models.PositiveIntegerField()
    replies = models.ManyToManyField('NotificationReply',
                                     related_name='replies',
                                     blank=True,
                                     null=True)
    for_objs = models.ManyToManyField('NotificationFor',
                                      related_name='for_objs',
                                      blank=True,
                                      null=True)
    source = models.CharField(max_length=20, choices=NotificationSource.CHOICES)
    objects = NotificationManager()

    class Meta:
        db_table = u'notifications'
        ordering = ('-created_dttm',)
        index_together = [
            ['about_content_type', 'about_id'],
        ]

    def add_reply(self, usr, text, reply_to_id=None):
        """Adds a reply to a Notification
        
        :param usr: the user the reply is from.
        :param text: the text for the reply.
        :param reply_to_id: is a reply to a specific reply.
        
        """
        # If the user isn't part of the for_objs they should be added because
        # they are not part of the conversation
        return self.notificationreply_set.create(created=usr,
                                                 last_modified=usr,
                                                 text=text,
                                                 reply_to_id=reply_to_id)

    def get_for_objects(self):
        """Gets the actual objects the notification is for."""
        return [obj.for_object
                for obj in self.for_objs.all().prefetch_related('for_object')]

    def get_replies(self):
        """Gets the notification reply objects for this notification."""
        return self.notificationreply_set.all()

    def get_reply_by_id(self, reply_id):
        """Gets the reply for a notification by it's id."""
        return self.notificationreply_set.get(id=reply_id)

    def delete_reply(self, reply_id):
        """Delete an individual notification reply.
        
        :param notification_id: ID of the notification reply to delete
        
        """
        self.notificationreply_set.filter(id=reply_id).delete()
        return True
