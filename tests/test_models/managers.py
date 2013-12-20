from django_notifications.managers import NotificationManager as BaseNotificationManager


class NotificationManager(BaseNotificationManager):
    """Test manager for overriding the Notification's manager."""

    def my_new_manager_method(self):
        return 'works'
