from __future__ import unicode_literals

from django.core.urlresolvers import reverse
from django_notifications.constants import NotificationSource
from django_notifications.models import Notification
from django_notifications.urls import urlpatterns
from django_testing.testcases.auth import AuthenticatedUserTestCase
from django_testing.testcases.urls import UrlTestCaseMixin
from django_testing.user_utils import create_user


class NotificationUrlTests(UrlTestCaseMixin, AuthenticatedUserTestCase):
    """Test case for ensuring all notification urls return a successful
    response.

    Note: This should probably be moved as a smoke test before deploying since
    this will be a much longer running test since it queries all the view
    mixins as well.
    """

    urlpatterns = urlpatterns

    @classmethod
    def setUpClass(cls):
        super(NotificationUrlTests, cls).setUpClass()
        cls.notification = cls.create_notification()
        cls.notification_reply = cls.notification.replies.create(
                                                created_user=cls.user,
                                                text='My reply',
                                                notification=cls.notification)

    @classmethod
    def create_notification(cls, text='Hello world',
                            source=NotificationSource.ACTIVITY,
                            created_user=None, **kwargs):
        about = create_user()
        return Notification.objects.create(
                                        created_user=created_user or cls.user,
                                        text=text,
                                        about=about,
                                        source=source,
                                        ensure_for_objs=cls.user,
                                        **kwargs)

    def test_notifications_view_view(self):
        """Test the notifications home url to ensure successful response."""
        url_args = [self.notification.about_content_type_id,
                    self.notification.about_id]
        self.response_test_get(reverse('notifications_view', args=url_args))

    def test_notification_view_view(self):
        """Test the notification view add page to ensure successful
        response.
        """
        self.response_test_get(self.notification.get_absolute_url())

    def test_notification_edit_view(self):
        """Test the notification edit view page to ensure successful
        response.
        """
        self.response_test_get(self.notification.get_edit_url())

    def test_notification_delete_view(self):
        """Test the notification delete view page to ensure successful
        response.
        """
        self.response_test_get(self.notification.get_delete_url())

    def test_notification_replies_view(self):
        """Test the notification replies view page to ensure successful
        response.
        """
        self.response_test_get(reverse('notification_replies',
                        args=[self.notification.id]))

    def test_notification_reply_view(self):
        """Test the notification reply view page to ensure successful
        response.
        """
        self.response_test_get(reverse('notification_reply',
                                           args=[self.notification.id,
                                                 self.notification_reply.id]))

    def test_notification_reply_edit_view(self):
        """Test the notification reply edit view page to ensure successful
        response.
        """
        self.response_test_get(reverse('notification_reply_edit',
                                           args=[self.notification.id,
                                                 self.notification_reply.id]))

    def test_notification_reply_delete_view(self):
        """Test the notification reply delete view page to ensure successful
        response.
        """
        self.response_test_get(reverse('notification_reply_delete',
                                           args=[self.notification.id,
                                                 self.notification_reply.id]))
