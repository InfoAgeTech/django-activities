from django.db import models


class AbstractNotificationMixin(models.Model):
    """Hook for adding additional functionality to the Notifications model
    without having to define a new model (proxy or otherwise).  Useful for
    adding things like project specific methods like url helpers:

    * get_absolute_url(...)
    """
    class Meta:
        abstract = True
