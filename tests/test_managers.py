from __future__ import unicode_literals

from activities.constants import Action
from activities.constants import Privacy
from activities.constants import Source
from activities.models import Activity
from django.test import TestCase
from django_testing.user_utils import create_user


class ActivityManagerTests(TestCase):
    """
    TODO: could break this up into smaller test cases that would test each
    individual section. Example:
        1. test for creating recurring bill
        2. test for verifying recurring bill activities exist
        3. test for update recurring bill
        4. test for deleting bill.
    """

    @classmethod
    def setUpClass(cls):
        """Run once per test case"""
        # TODO:
        #    1. add x number of users self.user_1, self.user_2...
        super(ActivityManagerTests, cls).setUpClass()
        cls.user = create_user()

    @classmethod
    def tearDownClass(cls):
        super(ActivityManagerTests, cls).tearDownClass()
        cls.user.delete()

    def test_create_activity(self):
        """Testing creating activities for a user."""
        text = 'hello world'
        source = Source.USER
        action = Action.COMMENTED
        activity = Activity.objects.create(created_user=self.user,
                                           text=text,
                                           about=self.user,
                                           source=source,
                                           action=action)
        for_objs = list(activity.get_for_objects())

        self.assertEqual(activity.about, self.user)
        self.assertEqual(activity.text, text)
        self.assertEqual(activity.source, source)
        self.assertEqual(activity.action, action)
        self.assertEqual(len(for_objs), 1)
        self.assertEqual(for_objs[0], self.user)

    def test_create_activity_ensure_for_obj(self):
        """Create a activity and make sure the ensure_for_obj is in
        the "for_objs" field.
        """
        user_2 = create_user()
        activity = Activity.objects.create(
            created_user=self.user,
            text='hello world',
            about=user_2,
            action=Action.COMMENTED,
            ensure_for_objs=[self.user, user_2]
        )
        for_objs = list(activity.get_for_objects())

        self.assertEqual(len(for_objs), 2)
        self.assertTrue(self.user in for_objs)
        self.assertTrue(user_2 in for_objs)

    def test_create_activity_ensure_for_objs(self):
        """Create a activity and make sure list of "ensure_for_objs" are in
        the "for_objs" field
        """
        user_2 = create_user()
        user_3 = create_user()
        activity = Activity.objects.create(
            created_user=self.user,
            text='hello world',
            about=user_2,
            action=Action.COMMENTED,
            ensure_for_objs=[self.user, user_2, user_3]
        )

        for_objs = list(activity.get_for_objects())
        self.assertEqual(len(for_objs), 3)
        self.assertTrue(self.user in for_objs)
        self.assertTrue(user_2 in for_objs)
        self.assertTrue(user_3 in for_objs)

    def test_get_for_object_no_user(self):
        """Test for gettting all activities for an object with no for_user
        passed in.
        """
        user_1 = create_user()
        activity = Activity.objects.create(
            created_user=self.user,
            text='hello world',
            about=user_1,
            action=Action.COMMENTED,
        )

        activities = Activity.objects.get_for_object(obj=user_1)
        self.assertEqual(len(activities), 1)
        self.assertEqual(activity, activities[0])

    def test_get_for_object_with_user(self):
        """Test for getting all activities for an object with for_user
        passed in.
        """
        user_1 = create_user()
        user_2 = create_user()
        activity = Activity.objects.create(
            created_user=self.user,
            text='hello world',
            about=user_1,
            action=Action.COMMENTED,
            ensure_for_objs=[user_2]
        )

        activities = Activity.objects.get_for_object(obj=user_1,
                                                     for_user=user_2)
        self.assertEqual(len(activities), 1)
        self.assertEqual(activity, activities[0])

    def test_get_for_object_with_user_not_qualifying_public(self):
        """Test for getting all activities for an object with for_user
        passed in (can see all public activities).
        """
        user_1 = create_user()
        user_2 = create_user()
        activity = Activity.objects.create(
            created_user=self.user,
            text='hello world',
            about=user_1,
            action=Action.COMMENTED
        )

        activities = Activity.objects.get_for_object(obj=user_1,
                                                     for_user=user_2)
        self.assertEqual(len(activities), 1)
        self.assertEqual(activity, activities[0])

    def test_get_for_object_with_user_not_qualifying_private(self):
        """Test for getting all activities for an object with for_user
        passed in who has access to a private activity. In other words, since
        the notification is private, it's only visible to the created user.
        """
        user_1 = create_user()
        user_2 = create_user()
        activity = Activity.objects.create(
            created_user=self.user,
            text='hello world',
            about=user_1,
            action=Action.COMMENTED,
            privacy=Privacy.PRIVATE,
            ensure_for_objs=[user_2]
        )

        activities = Activity.objects.get_for_object(obj=user_1,
                                                     for_user=user_2)
        self.assertEqual(len(activities), 0)

    def test_get_for_object_with_user_qualifying_custom(self):
        """Test for getting all activities for an object with for_user
        passed in who has access to a private activity.
        """
        user_1 = create_user()
        user_2 = create_user()
        activity = Activity.objects.create(
            created_user=self.user,
            text='hello world',
            about=user_1,
            action=Action.COMMENTED,
            privacy=Privacy.CUSTOM,
            ensure_for_objs=[user_2]
        )

        activities = Activity.objects.get_for_object(obj=user_1,
                                                     for_user=user_2)
        self.assertEqual(len(activities), 1)
        self.assertEqual(activity, activities[0])
