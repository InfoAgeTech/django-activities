[<img src="https://travis-ci.org/InfoAgeTech/django-activities.png?branch=master">](http://travis-ci.org/InfoAgeTech/django-activities)
[<img src="https://coveralls.io/repos/InfoAgeTech/django-activities/badge.png">](https://coveralls.io/r/InfoAgeTech/django-activities)

django-activities
====================
django-activities is a generic python activities module written for django.  You can create activities about any object type and share that comment with any object type.

Intallation
===========
Download the source from Github and run:

    pip install django-activities

Dependencies
============
* [django-core](https://github.com/InfoAgeTech/django-core)

Configuration
=============
Config steps:

1. Add to installed apps. django-activities has two dependencies which are listed above. Both need to be added to the installed apps in your settings file.:

        INSTALLED_APPS += (
            ...
            'django_core',
            'activities',
            ...
        )


By default, django-activities comes with builtin views.  You can use them if you like or totally write your own.

To use the views here are a few configuration steps to follow:

1. Create the html file that will be used as the gateway between your application templates and django-activities templates.  A simple template would look something like:
    
        # base_activities.html
        {% extends request.base_template %}
    
        {% block content %}
          {% block activities_content %}{% endblock %}
        {% endblock %}

2. Once you're created the base activities html file, you need to link to it in your settings.  In your settings file add the following setting that points to your template you just created:

        ACTIVITIES_BASE_TEMPLATE = 'path/to/your/template/base_activities.html'

3. Add the context processor in your settings that's used to retrieve your custom base template:

        TEMPLATE_CONTEXT_PROCESSORS = (
            ...
            'activities.context_processors.template_name',
            ...
        )

4. Add the urls (generic urls are not longer the recommended approach. see extending the urls section):

        urlpatterns = patterns('',
            ...
            url(r'^activities', include('activities.urls')),
            ...
        )

5. There are also default .less and .js files that will assist the activities as well.  These are optional and the js requires jquery.  The files are located at:

        /static/activities/js/activities.js
        /static/activities/less/activities.less


Custom Activity Urls
--------------------

There are times when you want prettier urls that aren't so generic or want to add additional subclasses to the activity views (like special permission checking view mixins).  If this is the case you'll need to do two things.  First, create a view that contains the mixin you want to use. Second, call the ``activities.urls.get_urls(...)`` method from within your urls.py file:
        
    # create the custom view that all activity views will inherit
    class MyCustomActivitiesView(object):
    
        def get_activities_about_object(self):
            # override the method to explicitly state which object
            # should be used for activies
            return some_object
    
Then in your urls.py:

    from activities.urls import get_urls
    from django.conf.urls import patterns
    
    urlpatterns = patterns('',
        ...
        # regular urls stuff
        url(r'^/foo/?$', SomeView.as_view(), name='my_view'),
        ...
    )
    
    # Generate the activity urls for movies
    get_urls(extend_urlpatterns=urlpatterns,
                root_urlpattern_name='my_view',
                class_prefix='MyActivies',
                bases_classes=(MyCustomActivitiesView,))

This will generate the following urls:

- /foo/activities
- /foo/activities/<activity_id>
- /foo/activities/<activity_id>/edit        
- /foo/activities/<activity_id>/delete
- etc

Form Rendering
--------------
Different apps render forms differently. With that in mind, this app lets you define the location for a function in your settings that will be used to render your forms.

For example,  if I want to use the [django-bootstrap-form](https://github.com/tzangms/django-bootstrap-form) app to render forms, I would provide the following setting to the template tag form rendering function:

    ACTIVITIES_FORM_RENDERER = 'bootstrapform.templatetags.bootstrap.bootstrap'

Then all forms will render using the django-bootstrap-form library.  You can optionally provide the following strings that will render that form using table, paragraph or list tags:

    ACTIVITIES_FORM_RENDERER = 'as_p'     # render form using <p> tags
    ACTIVITIES_FORM_RENDERER = 'as_table' # render form using <table>
    ACTIVITIES_FORM_RENDERER = 'as_ul'    # render form using <ul>

This will default to rending the form to however the form's ``__str__`` method is defined.

Examples
========
Below are some basic examples on how to use django-activities:

    >>> from django.contrib.auth import get_user_model
    >>> from activities.models import Activity
    >>>
    >>> User = get_user_model()
    >>> user = User.objects.create_user(username='hello')
    >>>
    >>> # The object the activity is about
    >>> about_obj = User.objects.create_user(username='world')
    >>> n = Activity.objects.create(created_user=user,
    ...                                 text='Hello world',
    ...                                 about=about_obj,
    ...                                 source='COMMENT')
    >>> n.text
    'Hello world'
    >>> user_activities = Activity.objects.get_for_user(user=user)
    >>> len(user_activities)
    1
    >>> object_activities = Activity.objects.get_for_object(obj=about_obj)
    >>> len(object_activities)
    1

Extend the Model
================
If all this configuration still isn't to your liking, then you can simply extend the Activity model:

    # my_activity_app/models.py
    
    from activities.models import AbstractActivity
    
    class MyActivity(AbstractActivity):
        """Your concrete implementation of the activity app."""
        # Do your stuff here

Custom Activity Rendering
=============================
When rendering the activities, the ``get_html`` will check to see if the activity ``about`` object has implemented custom rendering of the activity itself.  In order for the custom rendering to occur, the ``about`` object model needs to implement the class as follows:

    def get_activity_created_html(self, activity, **kwargs):
        """The activity renderer for a created activity about this object."""
        # do rendering that returns html
        return rendered_html

Tests
=====
From the ``tests`` directory where the manage.py file is, run:

    python manage.py test
