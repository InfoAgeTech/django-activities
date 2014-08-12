from __future__ import unicode_literals

from django.core.urlresolvers import reverse
from django_testing.testcases.auth import AuthenticatedUserTestCase
from django_testing.testcases.urls import UrlTestCaseMixin
from django_testing.user_utils import create_user

from activities.constants import Source
from activities.models import Activity
from activities.urls import urlpatterns


class ActivityUrlTests(UrlTestCaseMixin, AuthenticatedUserTestCase):
    """Test case for ensuring all activity urls return a successful
    response.

    Note: This should probably be moved as a smoke test before deploying since
    this will be a much longer running test since it queries all the view
    mixins as well.
    """

    urlpatterns = urlpatterns

    @classmethod
    def setUpClass(cls):
        super(ActivityUrlTests, cls).setUpClass()
        cls.activity = cls.create_activity()
        cls.activity_reply = cls.activity.replies.create(
            created_user=cls.user,
            text='My reply',
            activity=cls.activity
        )

    @classmethod
    def create_activity(cls, text='Hello world', source=Source.SYSTEM,
                        created_user=None, **kwargs):
        about = create_user()
        return Activity.objects.create(
            created_user=created_user or cls.user,
            text=text,
            about=about,
            source=source,
            ensure_for_objs=cls.user,
            **kwargs
        )

    def test_activities_view_view(self):
        """Test the activities home url to ensure successful response."""
        url_args = [self.activity.about_content_type_id,
                    self.activity.about_id]
        self.response_test_get(reverse('activities_view', args=url_args))

    def test_activity_view_view(self):
        """Test the activity view add page to ensure successful
        response.
        """
        self.response_test_get(self.activity.get_absolute_url())

    def test_activity_edit_view(self):
        """Test the activity edit view page to ensure successful
        response.
        """
        self.response_test_get(self.activity.get_edit_url())

    def test_activity_delete_view(self):
        """Test the activity delete view page to ensure successful
        response.
        """
        self.response_test_get(self.activity.get_delete_url())

    def test_activity_replies_view(self):
        """Test the activity replies view page to ensure successful
        response.
        """
        self.response_test_get(reverse('activity_replies',
                                       args=[self.activity.id]))

    def test_activity_reply_view(self):
        """Test the activity reply view page to ensure successful
        response.
        """
        self.response_test_get(reverse('activity_reply',
                                       args=[self.activity.id,
                                             self.activity_reply.id]))

    def test_activity_reply_edit_view(self):
        """Test the activity reply edit view page to ensure successful
        response.
        """
        self.response_test_get(reverse('activity_reply_edit',
                                       args=[self.activity.id,
                                             self.activity_reply.id]))

    def test_activity_reply_delete_view(self):
        """Test the activity reply delete view page to ensure successful
        response.
        """
        self.response_test_get(reverse('activity_reply_delete',
                                       args=[self.activity.id,
                                             self.activity_reply.id]))
