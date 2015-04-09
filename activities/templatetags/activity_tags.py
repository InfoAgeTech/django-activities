from __future__ import unicode_literals

from django.template import Library
from django.template.loader import render_to_string
from django_core.utils.loading import get_function_from_settings


register = Library()


@register.simple_tag(takes_context=True)
def render_activities(context, page, obj, activity_url, activity_source=None):
    """Renders an activities.

    :param page: the django page object of activities
    :param obj: the obj the activities are about
    :param activity_url: the url to use for the activities
    :param source: the activity source
    """
    template_context = {
        'activities_page': page,
        'obj': obj,
        'activity_url': activity_url
    }

    if activity_source is not None:
        template_context['activity_source'] = activity_source

    return render_to_string('activities/snippets/activities.html',
                            template_context,
                            context_instance=context)


@register.simple_tag(takes_context=True)
def render_activity(context, activity, activity_url, show_reference_obj=False):
    template_context = {
        'activity': activity,
        'show_reference_obj': show_reference_obj,
        'activity_url': activity_url
    }

    return render_to_string('activities/snippets/activity.html',
                            template_context,
                            context_instance=context)


@register.filter
def render_activity_form(form):
    """Renders a form based on settings ``ACTIVITIES_FORM_RENDERER``
    setting.  This allows users to plug in different 3rd party form rendering
    apps while being able to maintain a consistent look and feel across their
    site.

    The function must accept 1 argument which is the form to be rendered. No
    other args will be passed.

    For example,  if I want to use the
    `django-bootstrap-form <https://github.com/tzangms/django-bootstrap-form>`_
    app to render forms, I would provide the following setting to the template
    tag form rendering function::

        ACTIVITIES_FORM_RENDERER = 'bootstrapform.templatetags.bootstrap.bootstrap'

    Then all forms will render using the django-bootstrap-form library.  You
    can optionally provide the following strings that will render that form
    using table, paragraph or list tags::

        ACTIVITIES_FORM_RENDERER = 'as_p'     # render form using <p> tags
        ACTIVITIES_FORM_RENDERER = 'as_table' # render form using <table>
        ACTIVITIES_FORM_RENDERER = 'as_ul'    # render form using <ul>

    This will default to rending the form to however the form's ``__str__``
    method is defined.
    """
    renderer_func = get_function_from_settings('ACTIVITIES_FORM_RENDERER')
    if not renderer_func:
        return form

    if renderer_func == 'as_table':
        return form.as_table()

    if renderer_func == 'as_ul':
        return form.as_ul()

    if renderer_func == 'as_p':
        return form.as_p()

    return renderer_func(form)
