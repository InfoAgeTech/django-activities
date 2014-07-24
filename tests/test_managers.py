from __future__ import unicode_literals

from django.contrib.auth import get_user_model
from django.test import TestCase
from django_notifications.constants import NotificationSource
from django_notifications.models import Notification
from django_testing.user_utils import create_user


User = get_user_model()


class NotificationManagerTests(TestCase):
    """
    TODO: could break this up into smaller test cases that would test each
    individual section. Example:
        1. test for creating recurring bill
        2. test for verifying recurring bill notifications exist
        3. test for update recurring bill
        4. test for deleting bill.
    """

    @classmethod
    def setUpClass(cls):
        """Run once per test case"""
        # TODO:
        #    1. add x number of users self.user_1, self.user_2...
        super(NotificationManagerTests, cls).setUpClass()
        cls.user = create_user()

    @classmethod
    def tearDownClass(cls):
        super(NotificationManagerTests, cls).tearDownClass()
        cls.user.delete()

    def test_create_notification(self):
        """Testing creating notifications for a user."""
        text = 'hello world'
        source = NotificationSource.COMMENT
        notification = Notification.objects.create(created_user=self.user,
                                                     text=text,
                                                     about=self.user,
                                                     source=source)
        for_objs = list(notification.get_for_objects())

        self.assertEqual(notification.about, self.user)
        self.assertEqual(notification.text, text)
        self.assertEqual(notification.source, source)
        self.assertEqual(len(for_objs), 1)
        self.assertEqual(for_objs[0], self.user)

    def test_create_notification_ensure_for_obj(self):
        """Create a notification and make sure the ensure_for_obj is in
        the "for_objs" field.
        """
        user_2 = create_user()
        notification = Notification.objects.create(
                                            created_user=self.user,
                                            text='hello world',
                                            about=user_2,
                                            source=NotificationSource.COMMENT,
                                            ensure_for_objs=[self.user,
                                                             user_2])
        for_objs = list(notification.get_for_objects())

        self.assertEqual(len(for_objs), 2)
        self.assertTrue(self.user in for_objs)
        self.assertTrue(user_2 in for_objs)

    def test_create_notification_ensure_for_objs(self):
        """Create a notification and make sure list of "ensure_for_objs" are in
        the "for_objs" field
        """
        user_2 = create_user()
        user_3 = create_user()
        notification = Notification.objects.create(
                                            created_user=self.user,
                                            text='hello world',
                                            about=user_2,
                                            source=NotificationSource.COMMENT,
                                            ensure_for_objs=[self.user,
                                                             user_2,
                                                             user_3])

        for_objs = list(notification.get_for_objects())
        self.assertEqual(len(for_objs), 3)
        self.assertTrue(self.user in for_objs)
        self.assertTrue(user_2 in for_objs)
        self.assertTrue(user_3 in for_objs)
