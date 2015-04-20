from __future__ import unicode_literals

from django_core.views import JSONResponse

from .utils import get_activity_html


class ActivityResponse(JSONResponse):
    """Returns a HttpResponse for an event that causes a new activity to be
    generated.  The content of the response is the new activity. Returns a
    status of 200.

    Response content sample:

    {
        activity: "activity html",
        additional_content_key1: additional_content_value1
    }

    :param activity: activity doc
    :param additional_content: a dictionary of additional content that should
        be returned with the response.
    :return: HttpResponse with json encoded activity content.
    """
    def __init__(self, request, activity, status=200, additional_content=None,
                 **kwargs):

        if additional_content:
            content = additional_content
        else:
            content = {}

        content['activity'] = get_activity_html(request=request,
                                                activity=activity)
        super(ActivityResponse, self).__init__(content=content, status=status,
                                               **kwargs)
