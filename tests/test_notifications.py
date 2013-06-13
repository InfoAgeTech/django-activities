# -*- coding: utf-8 -*-
from django.contrib.auth import get_user_model
from django.test import TestCase
from django_notifications.constants import NotificationSource
from django_notifications.models import Notification
import uuid

User = get_user_model()
random_string = lambda len = None: uuid.uuid4().hex[:len or 10]


def create_user(username=None, email=None):
    if not username:
        username = random_string()

    if not email:
        email = '{0}@{1}.com'.format(random_string(), random_string())

    return User.objects.create_user(username=username,
                                    email=email)


class BaseNotificationTests(TestCase):

    @classmethod
    def setUpClass(cls):
        """Run once per test case"""
        super(BaseNotificationTests, cls).setUpClass()
        cls.user = create_user()

    @classmethod
    def tearDownClass(cls):
        super(BaseNotificationTests, cls).tearDownClass()
        cls.user.delete()

#    def setUp(self):
#        """Run once per test."""
# #        self.about_doc = MockDoc()
#        pass


class NotificationManagerTests(BaseNotificationTests):
    """Tests for the notification manager."""

    def test_create_notification(self):
        """
        Testing adding notifications for a user.
        """
        text = 'Hello world'
        about_obj = create_user()

        n = Notification.objects.create(created_user=self.user,
                                        text=text,
                                        about=about_obj,
                                        source=NotificationSource.COMMENT)

        self.assertEqual(n.about, about_obj)
        self.assertEqual(n.about_id, about_obj.id)
        self.assertEqual(n.source, NotificationSource.COMMENT)
        self.assertEqual(n.text, text)
        self.assertEqual(n.created, self.user)
        self.assertEqual(n.last_modified, self.user)

    def test_get_for_user(self):
        """Test get notifications for a user."""
        about_obj = create_user()
        for_user = create_user()

        n1 = Notification.objects.create(created_user=self.user,
                                         text='Hello world 1',
                                         about=about_obj,
                                         source=NotificationSource.COMMENT,
                                         ensure_for_objs=for_user)
        n2 = Notification.objects.create(created_user=self.user,
                                         text='Hello world 2',
                                         about=about_obj,
                                         source=NotificationSource.COMMENT,
                                         ensure_for_objs=for_user)
        n3 = Notification.objects.create(created_user=self.user,
                                         text='Hello world 3',
                                         about=about_obj,
                                         source=NotificationSource.COMMENT,
                                         ensure_for_objs=for_user)

        notifications = Notification.objects.get_for_user(user=for_user)

        self.assertEqual(len(notifications), 3)
        self.assertTrue(n1 in notifications)
        self.assertTrue(n2 in notifications)
        self.assertTrue(n3 in notifications)

    def test_get_for_object(self):
        """Test get notifications for a user."""
        about_obj = create_user()
        for_user = create_user()

        n1 = Notification.objects.create(created_user=self.user,
                                         text='Hello world 1',
                                         about=about_obj,
                                         source=NotificationSource.COMMENT,
                                         ensure_for_objs=for_user)
        n2 = Notification.objects.create(created_user=self.user,
                                         text='Hello world 2',
                                         about=about_obj,
                                         source=NotificationSource.COMMENT,
                                         ensure_for_objs=for_user)
        n3 = Notification.objects.create(created_user=self.user,
                                         text='Hello world 3',
                                         about=about_obj,
                                         source=NotificationSource.COMMENT,
                                         ensure_for_objs=for_user)

        notifications = Notification.objects.get_for_object(obj=for_user)

        self.assertEqual(len(notifications), 3)
        self.assertTrue(n1 in notifications)
        self.assertTrue(n2 in notifications)
        self.assertTrue(n3 in notifications)


class NotificationTests(BaseNotificationTests):
    """Tests for notifications."""

    def test_add_reply(self):
        """Test for adding notification replies."""
        n = Notification.objects.create(created_user=self.user,
                                        text='Hello world',
                                        about=create_user(),
                                        source=NotificationSource.COMMENT)
        replies = n.replies.all()
        self.assertEqual(len(replies), 0)

        reply_user = create_user()
        reply_text = 'Some reply comment.'

        reply = n.add_reply(usr=reply_user,
                            text=reply_text)

        self.assertEqual(reply.notification, n)
        self.assertEqual(reply.text, reply_text)
        self.assertEqual(reply.created, reply_user)
        self.assertEqual(reply.last_modified, reply_user)

        replies = n.get_replies()
        self.assertEqual(len(replies), 1)
        self.assertEqual(replies[0], reply)

    def test_get_for_objects(self):
        """Test getting the actual for objects."""
        text = 'Hello world'
        about_obj = create_user()

        n = Notification.objects.create(created_user=self.user,
                                        text=text,
                                        about=about_obj,
                                        source=NotificationSource.COMMENT)
        for_objects = n.get_for_objects()

        self.assertEqual(len(for_objects), 2)
        self.assertTrue(about_obj in for_objects)
        self.assertTrue(self.user in for_objects)

    def test_get_reply_by_id(self):
        """Test for adding notification replies."""
        n = Notification.objects.create(created_user=self.user,
                                        text='Hello world',
                                        about=create_user(),
                                        source=NotificationSource.COMMENT)

        reply_user = create_user()
        reply_text = 'Some reply comment.'

        reply = n.add_reply(usr=reply_user,
                            text=reply_text)

        reply_db = n.get_reply_by_id(reply_id=reply.id)

        self.assertEqual(reply, reply_db)

    def test_get_replies(self):
        """Test for adding notification replies."""
        n = Notification.objects.create(created_user=self.user,
                                        text='Hello world',
                                        about=create_user(),
                                        source=NotificationSource.COMMENT)

        reply1 = n.add_reply(usr=create_user(), text='Some reply comment.')
        reply2 = n.add_reply(usr=create_user(), text='Some reply comment.')
        reply3 = n.add_reply(usr=create_user(), text='Some reply comment.')
        reply4 = n.add_reply(usr=create_user(), text='Some reply comment.')

        replies = list(n.get_replies())

        self.assertEqual(len(replies), 4)
        self.assertTrue(reply1 in replies)
        self.assertTrue(reply2 in replies)
        self.assertTrue(reply3 in replies)
        self.assertTrue(reply4 in replies)

    def test_delete_reply(self):
        """Test for adding notification replies."""
        n = Notification.objects.create(created_user=self.user,
                                        text='Hello world',
                                        about=create_user(),
                                        source=NotificationSource.COMMENT)

        reply1 = n.add_reply(usr=create_user(), text='Some reply comment.')
        reply2 = n.add_reply(usr=create_user(), text='Some reply comment.')
        reply3 = n.add_reply(usr=create_user(), text='Some reply comment.')
        reply4 = n.add_reply(usr=create_user(), text='Some reply comment.')

        n.delete_reply(reply_id=reply3.id)

        replies = list(n.get_replies())

        self.assertEqual(len(replies), 3)
        self.assertTrue(reply1 in replies)
        self.assertTrue(reply2 in replies)
        self.assertTrue(reply4 in replies)
