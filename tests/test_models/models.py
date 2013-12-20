from django.db import models


class AbstractNotificationMixin(models.Model):
    """The abstract notification model to add functionality to the
    Notification's model.
    """

    class Meta:
        abstract = True

    def my_test_method(self):
        return 'worked'
