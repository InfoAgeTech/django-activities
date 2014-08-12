from __future__ import unicode_literals

from django.contrib.auth import get_user_model
from django.test import TestCase
from django_testing.user_utils import create_user

from activities.constants import Action
from activities.constants import Privacy
from activities.constants import Source
from activities.models import Activity
from activities.mixins.views import ActivityViewMixin
from mock import MagicMock
from django.http.response import Http404


User = get_user_model()


class ActivityManagerTests(TestCase):
    """
    TODO: could break this up into smaller test cases that would test each
    individual section. Example:
        1. test for creating recurring bill
        2. test for verifying recurring bill activities exist
        3. test for update recurring bill
        4. test for deleting bill.
    """

#     @classmethod
#     def setUpClass(cls):
#         """Run once per test case"""
#         # TODO:
#         #    1. add x number of users self.user_1, self.user_2...
#         super(ActivityManagerTests, cls).setUpClass()
#         cls.user = create_user()
#
#     @classmethod
#     def tearDownClass(cls):
#         super(ActivityManagerTests, cls).tearDownClass()
#         cls.user.delete()

    def test_activity_view_mixin_success(self):
        """Test ActivityViewMixin successfully returns the public activity."""
        user_2 = create_user()
        activity = Activity.objects.create(
            created_user=user_2,
            about=user_2,
            source=Source.USER,
            action=Action.COMMENTED,
            privacy=Privacy.PUBLIC
        )
        mixin = ActivityViewMixin()
        view_activity = mixin.get_activity(**{
            mixin.activity_pk_url_kwarg: activity.id
        })

        self.assertEqual(activity, view_activity)

    def test_activity_view_mixin_success_private(self):
        """Test ActivityViewMixin successfully returns the private activity."""
        user_2 = create_user()
        user_3 = create_user()
        activity = Activity.objects.create(
            created_user=user_2,
            about=user_2,
            source=Source.USER,
            action=Action.COMMENTED,
            privacy=Privacy.PRIVATE,
            ensure_for_objs=[user_3]
        )

        mixin = ActivityViewMixin()
        mixin.request = MagicMock(user=user_3)
        view_activity = mixin.get_activity(**{
            mixin.activity_pk_url_kwarg: activity.id
        })

        self.assertEqual(activity, view_activity)

    def test_activity_view_mixin_success_private_created_user(self):
        """Test ActivityViewMixin successfully returns the private activity
        that was created by the authenticated user.
        """
        user_2 = create_user()
        activity = Activity.objects.create(
            created_user=user_2,
            about=user_2,
            source=Source.USER,
            action=Action.COMMENTED,
            privacy=Privacy.PRIVATE
        )

        mixin = ActivityViewMixin()
        mixin.request = MagicMock(user=user_2)
        view_activity = mixin.get_activity(**{
            mixin.activity_pk_url_kwarg: activity.id
        })

        self.assertEqual(activity, view_activity)

    def test_activity_view_mixin_fail_404_private(self):
        """Test ActivityViewMixin returns a 404 since the user doesn't have
        access to the activity."""
        user_2 = create_user()
        user_3 = create_user()
        activity = Activity.objects.create(
            created_user=user_2,
            about=user_2,
            source=Source.USER,
            action=Action.COMMENTED,
            privacy=Privacy.PRIVATE
        )

        mixin = ActivityViewMixin()
        mixin.request = MagicMock(user=user_3)
        with self.assertRaises(Http404):
            mixin.get_activity(**{
                mixin.activity_pk_url_kwarg: activity.id
            })
