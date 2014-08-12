from django.conf import settings


def template_name(request):
    """Common settings to put in context."""
    template_path = getattr(settings,
                            'ACTIVITIES_BASE_TEMPLATE',
                            'activities/base_activities.html')
    return {
        'ACTIVITIES_BASE_TEMPLATE': template_path
    }
