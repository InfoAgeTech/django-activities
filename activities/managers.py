from __future__ import unicode_literals

from django.contrib.contenttypes.models import ContentType
from django.db.models.query_utils import Q
from django_core.db.models import CommonManager

from .constants import Action
from .constants import Privacy
from .constants import Source


class ActivityManager(CommonManager):
    """Manager for activities."""

    def create(self, created_user, text=None, about=None,
               source=Source.SYSTEM, action=Action.CREATED,
               ensure_for_objs=None, exclude_objs=None, **kwargs):
        """Creates a activity.

        :param created_user: the user document who created the activity.
        :param text: the text of the activity
        :param obj: the document this activity is for.
        :param source: the source of the activities. Can be one of
            contant.Source values.
        :param action: the action verb.  In this instance, it should almost
            always be CREATED
        :param ensure_for_objs: list of object to ensure will receive the
            activity.
        :param exclude_objs: exclude these objects from receiving the
            activity.
        :return: if activity is successfully added this returns True.
            Doesn't return entire object because the could potentially be a ton
            of activities and I won't want to return all of them.

        """
        if about is not None:
            kwargs['about'] = about

        n = super(ActivityManager, self).create(
            text=text.strip() if text else text,
            created_user=created_user,
            last_modified_user=created_user,
            source=source,
            action=action,
            **kwargs
        )

        for_objs = set([about])

        if ensure_for_objs:
            if not isinstance(ensure_for_objs, (list, tuple, set)):
                ensure_for_objs = set([ensure_for_objs])

            for_objs.update(ensure_for_objs)

        # Remove any objects that should be excluded from the activity
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
        """Gets activities for a user.

        :param user: the user to get the activities for

        """
        return self.get_for_object(obj=user, **kwargs)

    def get_for_object(self, obj, for_user=None, **kwargs):
        """Gets activities for a specific object.

        If ``for_user`` is provided, this will return all activities for the
        object that are public and will also return all private activities
        that the ``for_user`` has access to.

        Example use case, "Jane" is on "John's" profile page full of
        activities.  Jane is the for_user and accessing John's
        activities. John is the ``obj``. Jane will be able to see all public
        activities as well as any private activities she specifically
        has be granted access to see.

        :param obj: the object the activities are for
        :param for_user: only activities that this user can see
        :param kwargs: any key value pair fields that are on the model.

        """
        content_type = ContentType.objects.get_for_model(obj)
        queryset = self.filter(for_objs__content_type=content_type,
                               for_objs__object_id=obj.id,
                               **kwargs)

        if for_user is None or not for_user.is_authenticated():
            return queryset.filter(privacy=Privacy.PUBLIC).distinct()

        if for_user and for_user == obj:
            return queryset

        user_content_type = ContentType.objects.get_for_model(for_user)
        return queryset.filter(Q(created_user=for_user) |
                               Q(privacy=Privacy.PUBLIC) |
                               Q(privacy=Privacy.CUSTOM,
                                 for_objs__content_type=user_content_type,
                                 for_objs__object_id=for_user.id)).distinct()


class ActivityReplyManager(CommonManager):
    """Manager for activity replies."""

    def create(self, created_user, activity, text, reply_to=None,
               **kwargs):
        """Creates a new activity reply.

        :param created: the user creating the reply.
        :param activity: the activity this reply is about.
        :param text: the text of the activity.
        :param reply_to: the reply this reply is about.
        """
        return super(ActivityReplyManager, self).create(
            created_user=created_user,
            text=text,
            activity=activity,
            reply_to=reply_to,
            **kwargs
        )

    def get_by_activity(self, activity):
        """Gets all objects for a activity object."""
        try:
            return self.get(activity=activity)
        except self.model.DoesNotExist:
            return None

    def get_by_activity_id(self, activity_id):
        """Gets all objects by activity id."""
        try:
            return self.get(activity_id=activity_id)
        except self.model.DoesNotExist:
            return None
