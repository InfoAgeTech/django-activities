NOTE: This is not stable yet and will likely change!  Please don't use in production until the 1.0 release.

====================
django-notifications
====================
django-notifications is a generic python notifications module written for django.  You can create notifications about any object type and share that comment with any object type.

Build Status
============
.. image:: https://travis-ci.org/InfoAgeTech/django-notifications.png?branch=master
  :target: http://travis-ci.org/InfoAgeTech/django-notifications

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

Tests
=====
From the project root where the manage.py file is, run::

    python manage.py test
