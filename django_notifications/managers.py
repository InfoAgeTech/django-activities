from __future__ import unicode_literals

from django.contrib.contenttypes.models import ContentType
from django_core.db.models import CommonManager

from .constants import NotificationSource


class NotificationManager(CommonManager):
    """Manager for notifications."""

    def create(self, created_user, text, about=None,
               source=NotificationSource.ACTIVITY, ensure_for_objs=None,
               exclude_objs=None, **kwargs):
        """Creates a notification.

        :param created_user: the user document who created the notification.
        :param text: the text of the notification
        :param obj: the document this notification is for.
        :param source: the source of the notifications. Can be one of
            NotificationSource values.
        :param ensure_for_objs: list of object to ensure will receive the
            notification.
        :param exclude_objs: exclude these objects from receiving the
            notification.
        :return: if notification is successfully added this returns True.
            Doesn't return entire object because the could potentially be a ton
            of notifications and I won't want to return all of them.

        """
        if about is not None:
            kwargs['about'] = about

        n = super(NotificationManager, self).create(
                                            text=text.strip(),
                                            created_user=created_user,
                                            last_modified_user=created_user,
                                            source=source,
                                            **kwargs)

        for_objs = set([about])

        if ensure_for_objs:
            if not isinstance(ensure_for_objs, (list, tuple, set)):
                ensure_for_objs = set([ensure_for_objs])

            for_objs.update(ensure_for_objs)

        # Remove any objects that should be excluded from the notification
        if exclude_objs:
            for obj in exclude_objs:
                if obj in for_objs:
                    for_objs.remove(obj)

        for_model = self.model._get_many_to_many_model(field_name='for_objs')

        # This is a bit annoying.  So I have to loop through these 1 by 1
        # instead of using the bulk_create from the object manager because the
        # bulk_create statement doesn't return primary keys which is needed for
        # for_objs related manager add function call. See:
        # https://code.djangoproject.com/ticket/19527
        for_objs = [for_model.objects.get_or_create_generic(
                                                        content_object=obj)[0]
                    for obj in for_objs if obj is not None]

        n.for_objs.add(*for_objs)
        return n

    def get_for_user(self, user, **kwargs):
        """Gets notifications for a user.

        :param user: the user to get the notifications for

        """
        return self.get_for_object(obj=user, **kwargs)

    def get_for_object(self, obj, for_user=None, **kwargs):
        """Gets notifications for a specific object.

        :param obj: the object the notifications are for
        :param for_user: only notifications that this user can see
        :param kwargs: any key value pair fields that are on the model.

        """
        content_type = ContentType.objects.get_for_model(obj)
        queryset = self.filter(for_objs__content_type=content_type,
                               for_objs__object_id=obj.id,
                               **kwargs)

        if for_user == None:
            return queryset

        user_content_type = ContentType.objects.get_for_model(for_user)
        return queryset.filter(for_objs__content_type=user_content_type,
                               for_objs__object_id=for_user.id)


class NotificationReplyManager(CommonManager):
    """Manager for notification replies."""

    def create(self, created_user, notification, text, reply_to=None,
               **kwargs):
        """Creates a new notification reply.

        :param created: the user creating the reply.
        :param notification: the notification this reply is about.
        :param text: the text of the notification.
        :param reply_to: the reply this reply is about.
        """
        return super(NotificationReplyManager, self).create(
                                                created_user=created_user,
                                                text=text,
                                                notification=notification,
                                                reply_to=reply_to,
                                                **kwargs)

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
