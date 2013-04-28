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

    @classmethod
    def add(cls, created_user, about_notification, text, reply_to_id=None):
        """Adds a new notification reply.
        
        :param created_user: the user creating the reply.
        :param about_notification: the notification this reply is about.
        :param text: the text of the notification.
        :param reply_to_id: the id of the reply this reply is about.
        """
        return cls.objects.create(created=created_user,
                                  text=text,
                                  reply_to_id=reply_to_id)


# TODO: Rename this to something like "NotificationRelations" since it includes the
# objects that are related to a notification.
class NotificationFor(models.Model):
    """Defines the generic object a notification is related to.
    
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

    @classmethod
    def add(cls, created_user, text, about, source, ensure_for_objs=None):
        """Adds a notification.
        
        TODO: Should this be on the manager? Notifications.objects.add(...)
        
        :param created_user: the user document who created the notification.
        :param text: the text of the notification
        :param obj: the document this notification is for.
        :param source: the source of the notifications. Can be one of 
            NotificationSource values.
        :param ensure_for_objs: list of object to ensure will receive the 
            notification.
        :return: if notification is successfully added this returns True.  
            Doesn't return entire object because the could potentially be a ton
            of notifications and I won't want to return all of them.
        
        """
        n = cls.objects.create(text=text.strip(),
                               about=about,
                               created=created_user,
                               last_modified=created_user,
                               source=source)

        for_objs = [about, created_user]

        if ensure_for_objs:
            if not isinstance(ensure_for_objs, (list, tuple)):
                ensure_for_objs = [ensure_for_objs]

            for_objs += ensure_for_objs

        # This is a bit annoying.  So I have to loop through these 1 by 1 instead
        # of using the bulk_create from the object manager because the bulk_create
        # statement doesn't return primary keys which is needed for for_objs
        # related manager add function call. See:
        # https://code.djangoproject.com/ticket/19527
        for_objs = [NotificationFor.objects.get_or_create_generic(obj=obj)[0]
                    for obj in set(for_objs)]

        # for_objs = NotificationFor.objects.bulk_create(for_objs)
        n.for_objs.add(*for_objs)
        return n

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
        return [obj.for_object for obj in self.for_objs.all()]

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
        # TODO: this might be:
        # self.notificationreplies_set.remove(id=reply_id)
        self.replies.remove(id=reply_id)
        return True


"""
The issue here is how you access all objects.  Could add a method of 
"get_for_objects(self, ...)" that get's all the object for me.

Or, just use for objects as more of a way to query vs actually show what's 
the objects are.


In [17]: n.for_objs
Out[17]: <django.db.models.fields.related.ManyRelatedManager at 0x102fd7990>

In [18]: n.for_objs.all()
Out[18]: [<NotificationFor: NotificationFor object>, <NotificationFor: NotificationFor object>]

In [19]: n.for_objs.all()[0].for_object
Out[19]: <User: f0a8e1f8d12046528824b29447d244e1>

In [20]: [obj.for_object for obj in n.for_objs.all()[0]]
---------------------------------------------------------------------------
TypeError                                 Traceback (most recent call last)
/Users/troy/.virtualenvs/bb_pg/lib/python2.7/site-packages/django/core/management/commands/shell.pyc in <module>()
----> 1 [obj.for_object for obj in n.for_objs.all()[0]]

TypeError: 'NotificationFor' object is not iterable

In [21]: [obj.for_object for obj in n.for_objs.all()]
Out[21]:
[<User: f0a8e1f8d12046528824b29447d244e1>,
 <User: c3750f8f6ed6488598f6dca47d621b12>]
"""
