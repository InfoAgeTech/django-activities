from django.db import models


class AbstractActivityMixin(models.Model):
    """The abstract activity model to add functionality to the
    Activity's model.
    """

    class Meta:
        abstract = True

    def my_test_method(self):
        return 'worked'
