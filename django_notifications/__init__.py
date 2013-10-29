# -*- coding: utf-8 -*-
from django.core.exceptions import ImproperlyConfigured


def get_notification_model():
    """Return the Notification model that is active in this project.

    This is the same pattern user for django's "get_user_model()" method. To
    allow you to set the model instance to a different model subclass.
    """
    from django.conf import settings
    from django.db.models import get_model

    if not hasattr(settings, 'NOTIFICATION_MODEL'):
        from .models import Notification
        return Notification

    try:
        app_label, model_name = settings.NOTIFICATION_MODEL.split('.')
    except ValueError:
        raise ImproperlyConfigured("NOTIFICATION_MODEL must be of the form 'app_label.model_name'")

    notification_model = get_model(app_label, model_name)

    if notification_model is None:
        raise ImproperlyConfigured("NOTIFICATION_MODEL refers to model '%s' that has not been installed" % settings.USER_CONNECTION_MODEL)

    return notification_model
