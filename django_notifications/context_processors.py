from django.conf import settings


def template_name(request):
    """Common settings to put in context."""
    template_path = getattr(settings,
                            'NOTIFICATIONS_BASE_TEMPLATE',
                            'notifications/base_notifications.html')
    return {
        'NOTIFICATIONS_BASE_TEMPLATE': template_path
    }
