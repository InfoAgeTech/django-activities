from activities.managers import ActivityManager as BaseActivityManager


class ActivityManager(BaseActivityManager):
    """Test manager for overriding the Activity's manager."""

    def my_new_manager_method(self):
        return 'works'
