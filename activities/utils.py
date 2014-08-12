from __future__ import unicode_literals

from django.template.context import RequestContext
from django.template.loader import render_to_string

try:
    # python 2
    import urlparse as parse
except ImportError:
    # python 3
    from urllib import parse


def get_activity_html(request, activity):
    """Gets the html for a activity.

    :param activity: activity document
    """
    context = {'activity': activity}

    # TODO: Need to fix all the url logic checking below since the
    #       absolute url != to the http referrer.
#     try:
#         about_obj_absolute_url = activity.about.get_absolute_url()
#         activity_url = '{0}/activities'.format(about_obj_absolute_url)
#     except:
#         about_obj_absolute_url = None
#         activity_url = None
#
#     current_url = parse.urlsplit(request.META.get('HTTP_REFERER', '')).path
#
#     if (about_obj_absolute_url != current_url and
#         activity_url not in current_url):
#         context['show_reference_obj'] = True

    return render_to_string('activities/snippets/activity.html',
                            context,
                            context_instance=RequestContext(request)).strip()
