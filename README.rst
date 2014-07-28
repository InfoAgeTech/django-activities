NOTE: This is not stable yet and will likely change!  Please don't use in production until the 1.0 release.

.. image:: https://travis-ci.org/InfoAgeTech/django-notifications.png?branch=master
    :target: http://travis-ci.org/InfoAgeTech/django-notifications
.. image:: https://coveralls.io/repos/InfoAgeTech/django-notifications/badge.png
    :target: https://coveralls.io/r/InfoAgeTech/django-notifications

====================
django-notifications
====================
django-notifications is a generic python notifications module written for django.  You can create notifications about any object type and share that comment with any object type.

Intallation
===========
Download the source from Github and run::

    python setup.py install

Dependencies
============
* `django-generic <https://github.com/InfoAgeTech/django-generic>`_
* `django-core <https://github.com/InfoAgeTech/django-core>`_

Configuration
=============
Config steps:

1. Add to installed apps. django-notifications has two dependencies which are listed above. Both need to be added to the installed apps in your settings file.::

    INSTALLED_APPS += (
        ...
        'django_core',
        'django_generic',
        'django_notifications',
        ...
    )


By default, django-notifications comes with builtin views.  You can use them if you like or totally write your own.

To use the views here are a few configuration steps to follow:

1. Create the html file that will be used as the gateway between your application templates and django-notifications templates.  A simple template would look something like::
    
    # base_notifications.html
    {% extends request.base_template %}

    {% block content %}
      {% block notifications_content %}{% endblock %}
    {% endblock %}

2. Once you're created the base notifications html file, you need to link to it in your settings.  In your settings file add the following setting that points to your template you just created::

    NOTIFICATIONS_BASE_TEMPLATE = 'path/to/your/template/base_notifications.html'

3. Add the context processor in your settings that's used to retrieve your custom base template::

    TEMPLATE_CONTEXT_PROCESSORS = (
        ...
        'django_notifications.context_processors.template_name',
        ...
    )

4. Add the urls::

    urlpatterns = patterns('',
        ...
        url(r'^notifications', include('django_notifications.urls')),
        ...
    )

5. There are also default .less and .js files that will assist the notifications as well.  These are optional and the js requires jquery.  The files are located at::

    /static/django_notifications/js/notifications.js
    /static/django_notifications/less/notifications.less

Form Rendering
--------------
Different apps render forms differently. With that in mind, this app lets you define the location for a function in your settings that will be used to render your forms.

For example,  if I want to use the `django-bootstrap-form <https://github.com/tzangms/django-bootstrap-form>`_ app to render forms, I would provide the following setting to the template tag form rendering function::

    NOTIFICATIONS_FORM_RENDER = 'bootstrapform.templatetags.bootstrap.bootstrap'

Then all forms will render using the django-bootstrap-form library.  You can optionally provide the following strings that will render that form using table, paragraph or list tags::

    NOTIFICATIONS_FORM_RENDER = 'as_p'     # render form using <p> tags
    NOTIFICATIONS_FORM_RENDER = 'as_table' # render form using <table>
    NOTIFICATIONS_FORM_RENDER = 'as_ul'    # render form using <ul>

This will default to rending the form to however the form's ``__str__`` method is defined.

Examples
========
Below are some basic examples on how to use django-notifications::

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
