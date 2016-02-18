from activities.constants import Action
from activities.constants import Privacy
from activities.models import Activity
from django_testing.user_utils import create_user


def create_activity(about, created_user=None, text='hello world',
                    action=Action.COMMENTED, privacy=Privacy.PRIVATE,
                    ensure_for_objs=None, **kwargs):
    """Creates an activity."""
    kwargs.update({
        'created_user': created_user or create_user(),
        'about': about,
        'action': action,
        'text': text,
        'privacy': privacy,
        'ensure_for_objs': ensure_for_objs or [],
    })
    return Activity.objects.create(**kwargs)
