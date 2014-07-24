from __future__ import unicode_literals

from django_core.views import JsonResponse

from .utils import get_notification_html


class NotificationResponse(JsonResponse):
    """Returns a HttpResponse for an event that causes a new notification to be
    generated.  The content of the response is the new notification. Returns a
    status of 200.

    Response content sample:

    {
        notification: "notification html",
        additional_content_key1: additional_content_value1
    }

    :param notification: notification doc
    :param additional_content: a dictionary of additional content that should be
        returned with the response.
    :return: HttpResponse with json encoded notification content.
    """
    def __init__(self, request, notification, status=200, additional_content=None):

        if additional_content:
            content = additional_content
        else:
            content = {}

        content['notification'] = get_notification_html(request=request,
                                                        notification=notification)
        super(NotificationResponse, self).__init__(content=content,
                                                       status=status)
