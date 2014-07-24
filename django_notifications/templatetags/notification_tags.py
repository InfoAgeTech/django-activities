from django.template import Library
from django.template.loader import render_to_string


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
    # TODO: if you have the page obj, then you already have the paginator (no need to pass it again)
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
