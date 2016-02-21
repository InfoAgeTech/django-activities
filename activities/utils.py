from django.template.context import RequestContext
from django.template.loader import render_to_string


def get_activity_html(request, activity):
    """Gets the html for a activity.

    :param activity: activity document
    """
    context = RequestContext(request)
    context.update({
        'activity': activity
    })

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
    if activity.about and hasattr(activity.about, 'get_activities_url'):
        context['activity_url'] = activity.about.get_activities_url()

    return render_to_string('activities/snippets/activity.html',
                            context=context).strip()


def get_activity_reply_html(request, activity_reply):
    """Gets the html for an activity reply.

    :param activity_reply: the activity reply to render the html for.
    """
    context = {
        'activity_reply': activity_reply,
        'user': request.user
    }

    return render_to_string('activities/snippets/activity_reply.html',
                            context=context).strip()
