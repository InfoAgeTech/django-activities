from activities import get_activity_model
from activities.constants import Privacy
from django.db import models


class AbstractActivityModelMixin(models.Model):
    """Model mixin for objects that can create Activity objects about
    themselves.
    """

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
