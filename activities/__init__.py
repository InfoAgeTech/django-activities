from __future__ import unicode_literals

from django.core.exceptions import ImproperlyConfigured


def get_activity_model():
    """Return the Activity model that is active in this project.

    This is the same pattern user for django's "get_user_model()" method. To
    allow you to set the model instance to a different model subclass.
    """
    from django.conf import settings
    from django.db.models import get_model

    if not hasattr(settings, 'ACTIVITY_MODEL'):
        from .models import Activity
        return Activity

    try:
        app_label, model_name = settings.ACTIVITY_MODEL.split('.')
    except ValueError:
        raise ImproperlyConfigured("ACTIVITY_MODEL must be of the form "
                                   "'app_label.model_name'")

    activity_model = get_model(app_label, model_name)

    if activity_model is None:
        raise ImproperlyConfigured("ACTIVITY_MODEL refers to model '%s' "
                                   "that has not been installed" %
                                   settings.ACTIVITY_MODEL)

    return activity_model
