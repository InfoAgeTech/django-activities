from __future__ import unicode_literals

from django.template.context import RequestContext
from django.template.loader import render_to_string

try:
    # python 2
    import urlparse as parse
except:
    # python 3
    from urllib import parse


def get_notification_html(request, notification):
    """Gets the html for a notification.

    :param notification: notification document
    """
    context = {'notification': notification}

    # TODO: Need to fix all the url logic checking below since the
    #       absolute url != to the http referrer.
    try:
        about_obj_absolute_url = notification.about.get_absolute_url()
        notification_url = '{0}/notifications'.format(about_obj_absolute_url)
    except:
        about_obj_absolute_url = None
        notification_url = None

    current_url = parse.urlsplit(request.META.get('HTTP_REFERER', '')).path

    if (about_obj_absolute_url != current_url and
        notification_url not in current_url):
        context['show_reference_obj'] = True

    return render_to_string('django_notifications/snippets/notification.html',
                            context,
                            context_instance=RequestContext(request)).strip()
