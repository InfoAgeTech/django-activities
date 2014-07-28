from __future__ import unicode_literals

from django.template import Library
from django.template.loader import render_to_string
from django_core.utils.loading import get_function_from_settings


register = Library()


@register.simple_tag(takes_context=True)
def render_notifications(context, page, obj, notification_url,
                         notification_source=None):
    """Renders an notifications.

    :param page: the django page object of notifications
    :param obj: the obj the notifications are about
    :param notification_url: the url to use for the notifications
    :param source: the notification source
    """
    template_context = {
        'notifications_page': page,
        'obj': obj,
        'notification_url': notification_url
    }

    if notification_source is not None:
        template_context['notification_source'] = notification_source

    return render_to_string('django_notifications/snippets/notifications.html',
                            template_context,
                            context_instance=context)


@register.simple_tag(takes_context=True)
def render_notification(context, notification, show_reference_obj=False):
    template_context = {
        'notification': notification,
        'show_reference_obj': show_reference_obj
    }

    return render_to_string('django_notifications/snippets/notification.html',
                            template_context,
                            context_instance=context)


@register.filter
def render_notification_form(form):
    """Renders a form based on settings ``NOTIFICATIONS_FORM_RENDER``
    setting.  This allows users to plug in different 3rd party form rendering
    apps while being able to maintain a consistent look and feel across their
    site.

    The function must accept 1 argument which is the form to be rendered. No
    other args will be passed.

    For example,  if I want to use the
    `django-bootstrap-form <https://github.com/tzangms/django-bootstrap-form>`_
    app to render forms, I would provide the following setting to the template
    tag form rendering function::

        NOTIFICATIONS_FORM_RENDER = 'bootstrapform.templatetags.bootstrap.bootstrap'

    Then all forms will render using the django-bootstrap-form library.  You
    can optionally provide the following strings that will render that form
    using table, paragraph or list tags::

        NOTIFICATIONS_FORM_RENDER = 'as_p'     # render form using <p> tags
        NOTIFICATIONS_FORM_RENDER = 'as_table' # render form using <table>
        NOTIFICATIONS_FORM_RENDER = 'as_ul'    # render form using <ul>

    This will default to rending the form to however the form's ``__str__``
    method is defined.
    """
    renderer_func = get_function_from_settings('NOTIFICATIONS_FORM_RENDER')
    if not renderer_func:
        return form

    if renderer_func == 'as_table':
        return form.as_table()

    if renderer_func == 'as_ul':
        return form.as_ul()

    if renderer_func == 'as_p':
        return form.as_p()

    return renderer_func(form)
