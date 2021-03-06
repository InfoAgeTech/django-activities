from activities.constants import Action
from django.contrib.contenttypes.models import ContentType
from django.db.models.query_utils import Q
from django_core.db.models import CommonManager

from .constants import Privacy
from .constants import Source
from django_core.db.models.managers import GenericManager


class ActivityManager(CommonManager):
    """Manager for Activity model."""

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

        for_objs = set([about])

        # if the action is SHARED, then first a check needs to be made to see
        # if that user already shared the content since it can only be shared
        # once per user.
        if action == Action.SHARED:
            for_objs.add(created_user)
            activity = self.model.objects.get_about_object(
                action=Action.SHARED,
                created_user=created_user,
                about=about
            ).first()

            if activity:
                # an activity exist for this user criteria. Just return it.
                return activity

        if ('privacy' not in kwargs and
            about and
            hasattr(about, 'privacy') and
            about.privacy in (Privacy.PRIVATE, Privacy.PUBLIC)):
            # set the privacy to be the privacy of the "about" object
            kwargs['privacy'] = about.privacy

        activity = super(ActivityManager, self).create(
            text=text.strip() if text else text,
            created_user=created_user,
            last_modified_user=created_user,
            source=source,
            action=action,
            **kwargs
        )

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

        activity.for_objs.add(*for_objs)
        return activity

    def get_about_object(self, about, **kwargs):
        """Gets all activities about the "about" object."""
        content_type = ContentType.objects.get_for_model(about)
        return self.filter(about_id=about.id,
                           about_content_type=content_type,
                           **kwargs)

    def get_for_user(self, user, **kwargs):
        """Gets activities for a user.

        :param user: the user to get the activities for

        """
        return self.get_for_object(obj=user, for_user=user, **kwargs)

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
            if 'privacy' not in kwargs:
                queryset = queryset.filter(privacy=Privacy.PUBLIC)

            return queryset.distinct()

        if for_user and for_user == obj:
            return queryset

        user_content_type = ContentType.objects.get_for_model(for_user)
        return queryset.filter(Q(created_user=for_user) |
                               Q(privacy=Privacy.PUBLIC) |
                               Q(privacy__in=[Privacy.CUSTOM, Privacy.PRIVATE],
                                 for_objs__content_type=user_content_type,
                                 for_objs__object_id=for_user.id)).distinct()

    def delete_all_about_object(self, about, **kwargs):
        """Deletes all activities about an object.

        :param about: the object to delete all activities for when this object
            is the "about" object on the activity.
        """
        content_type = ContentType.objects.get_for_model(about)
        return self.filter(about_content_type=content_type,
                           about_id=about.id).delete()

    def updates_for_about_objects_queryset(self, about_objects_queryset,
                                            **updates):
        """Update activites for "about" objects from a queryset of "about"
        objects.

        :param about_objects_queryset: the queryset of activity "about" objects
            to update.
        """
        if not updates:
            return None

        content_type = ContentType.objects.get_for_model(
            about_objects_queryset.model
        )

        activities_queryset = self.filter(
            about_content_type=content_type,
            about_id__in=about_objects_queryset.values_list('id', flat=True)
        )

        if len(updates.keys()) == 1:
            # exclude items that don't need to be updates because they already
            # have the one change needed
            activities_queryset = activities_queryset.exclude(**updates)

        return activities_queryset.update(**updates)

    def updates_for_about_object(self, about, **updates):
        """Make updates to activites for activities with the "about" object.

        :param about: updates all activities that have this "about" object
        """
        if not updates:
            return None

        content_type = ContentType.objects.get_for_model(about)

        return self.filter(
            about_content_type=content_type,
            about_id=about.id
        ).update(**updates)


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


class ActivityForManager(GenericManager, CommonManager):
    """Model manager for the ActivityFor model."""

    def get_for_object(self, obj, **kwargs):
        """Gets instance for the obj.

        :param obj: the object to get the ActivityFor instances for.
        """
        content_type = ContentType.objects.get_for_model(obj)

        return self.filter(
            content_type=content_type,
            object_id=obj.id,
            **kwargs
        )
