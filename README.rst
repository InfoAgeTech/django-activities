NOTE: This is not stable yet and will likely change!  Please don't use in production until the 1.0 release.

.. |travisci| image:: https://travis-ci.org/InfoAgeTech/django-notifications.png?branch=master
  :target: http://travis-ci.org/InfoAgeTech/django-notifications
.. |coveralls| image:: https://coveralls.io/repos/InfoAgeTech/django-notifications/badge.png
  :target: https://coveralls.io/r/InfoAgeTech/django-notifications

===========================================
django-notifications |travisci| |coveralls|
===========================================
django-notifications is a generic python notifications module written for django.  You can create notifications about any object type and share that comment with any object type.

Intallation
===========
Download the source from Github and run::

    python setup.py install

Dependencies
============
* `django-generic <https://github.com/InfoAgeTech/django-generic>`_
* `django-tools <https://github.com/InfoAgeTech/django-tools>`_

Examples
========
Below are some basic examples on how to user django-notifications::

    >>> from django.contrib.auth import get_user_model
    >>> from django_notifications.models import Notification
    >>>
    >>> User = get_user_model()
    >>> user = User.objects.create_user(username='hello')
    >>>
    >>> # The object the notification is about
    >>> about_obj = User.objects.create_user(username='world')
    >>> n = Notification.objects.create(created_user=user,
    ...                                 text='Hello world',
    ...                                 about=about_obj,
    ...                                 source='COMMENT')
    >>> n.text
    'Hello world'
    >>> user_notifications = Notification.objects.get_for_user(user=user)
    >>> len(user_notifications)
    1
    >>> object_notifications = Notification.objects.get_for_object(obj=about_obj)
    >>> len(object_notifications)
    1

Extending the Notification Model
================================
There are times when a generic 3rd party model doesn't quite give you all the functionality you'd like.  Things like project specific settings or adding helper functions like::

    def get_absolute_url(...)

This app give you the ability to add a mixin to the Notification model to alter it's behavior.

Creating the Model Mixin
------------------------
Create the mixin you want to apply to the Notification model::

    # my_notification_app/models.py
    from django.db import models
    
    class AbstractNotificationMixin(models.Model):
        """The abstract notification model to add functionality to the
        Notification's model.
        """
    
        class Meta:
            abstract = True
        
        def get_absolute_url(self):
            return reverse('my_notification_url_name', args=[self.id])
        
        def my_new_method(self):
            # do something with the notification object
            return 'works'

Configuring the Mixin
---------------------
In your django settings.py file, include the ``NOTIFICATION_MODEL_MIXIN`` that points to your notification model mixin::

    NOTIFICATION_MODEL_MIXIN = 'my_notifications_app.AbstractNotificationMixin'
    
Using the New Model
-------------------
Now that the mixin has been created and configured, let's use it::

    >>> from django_notifications.models import Notification
    >>> n = Notification()
    >>> n.my_new_method()
    'works'

Using a Custom Model Manager
============================
There are also times when you want to customize a model manager, but don't want to create another concrete implementation or proxy model.  Here's how you extend or override the object manager model.

Creating the Model Manager
--------------------------
Create the manager you want to user for the Notification model::

    # my_notification_app/managers.py
    from django_notifications.managers import NotificationManager


    class MyNotificationManager(NotificationManager):
        """Manager for overriding the Notification's manager."""

        def my_new_manager_method(self):
            return 'works'


Configuring the Manager
-----------------------
In your django settings.py file, include the ``NOTIFICATION_MANAGER`` that points to notification manager you want to use for the project::

    NOTIFICATION_MANAGER = 'my_notifications_app.managers.MyNotificationManager'
    
Using the New Manager
---------------------
Now that the manager has been created and configured, let's use it::
    
    >>> from django_notifications.models import Notification
    >>> n = Notification.objects.my_new_manager_method()
    'works'

Extend the Model
================
If all this configuration still isn't to your liking, then you can simply extend the Notification model::

    # my_notification_app/models.py
    
    from django_notifications.models import AbstractNotification
    
    class MyNotification(AbstractNotification):
        """Your concrete implementation of the notification app."""
        # Do your stuff here

Tests
=====
From the ``tests`` directory where the manage.py file is, run::

   python manage.py test
