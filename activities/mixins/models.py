from activities import get_activity_model
from activities.constants import Privacy
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models


class AbstractActivityModelMixin(models.Model):
    """Model mixin for objects that can create Activity objects about
    themselves.
    """
    activities = GenericRelation('activities.Activity',
                                 object_id_field='about_id',
                                 content_type_field='about_content_type')

    class Meta():
        abstract = True

    def create_activity(self, created_user, source, action,
                        privacy=Privacy.PRIVATE, **kwargs):
        """Creates an activity about this object.

        :param created_user: the user creating the activity.
        :param source: the source of the activity.  Can be one of
            activities.constants.Source values.
        :param action: the action that was taken to create the activity.  Can be
            one of activities.constants.Action values.
        """
        Activity = get_activity_model()
        return Activity.objects.create(
            about=self,
            action=action,
            created_user=created_user,
            source=source,
            privacy=privacy,
            **kwargs
        )

    @classmethod
    def post_delete(cls, sender, instance, **kwargs):
        """Ensures that the actual image file itself is deleted if one
        exists.
        """
        super(AbstractActivityModelMixin, cls).post_delete(sender, instance,
                                                           **kwargs)
        # need to delete any notifications about this object
        get_activity_model().objects.delete_all_about_object(about=instance)
