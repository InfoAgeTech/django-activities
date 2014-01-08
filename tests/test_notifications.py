# -*- coding: utf-8 -*-
from django.contrib.auth import get_user_model
from django_notifications import get_notification_model
from django_notifications.constants import NotificationSource
from django_testing.testcases.users import SingleUserTestCase
from django_testing.user_utils import create_user


User = get_user_model()
Notification = get_notification_model()


class NotificationManagerTests(SingleUserTestCase):
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
        self.assertEqual(n.created_user, self.user)
        self.assertEqual(n.last_modified_user, self.user)

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
                                         ensure_for_objs=[self.user, for_user])
        n2 = Notification.objects.create(created_user=self.user,
                                         text='Hello world 2',
                                         about=about_obj,
                                         source=NotificationSource.COMMENT,
                                         ensure_for_objs=[self.user, for_user])
        n3 = Notification.objects.create(created_user=self.user,
                                         text='Hello world 3',
                                         about=about_obj,
                                         source=NotificationSource.COMMENT,
                                         ensure_for_objs=[self.user, for_user])

        notifications = Notification.objects.get_for_object(obj=for_user)

        self.assertEqual(len(notifications), 3)
        self.assertTrue(n1 in notifications)
        self.assertTrue(n2 in notifications)
        self.assertTrue(n3 in notifications)


class NotificationTests(SingleUserTestCase):
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

        reply = n.add_reply(user=reply_user,
                            text=reply_text)

        self.assertEqual(reply.notification, n)
        self.assertEqual(reply.text, reply_text)
        self.assertEqual(reply.created_user, reply_user)
        self.assertEqual(reply.last_modified_user, reply_user)

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
                                        source=NotificationSource.COMMENT,
                                        ensure_for_objs=self.user)
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

        reply = n.add_reply(user=reply_user,
                            text=reply_text)

        reply_db = n.get_reply_by_id(reply_id=reply.id)

        self.assertEqual(reply, reply_db)

    def test_get_replies(self):
        """Test for adding notification replies."""
        n = Notification.objects.create(created_user=self.user,
                                        text='Hello world',
                                        about=create_user(),
                                        source=NotificationSource.COMMENT)

        reply1 = n.add_reply(user=create_user(), text='Some reply comment.')
        reply2 = n.add_reply(user=create_user(), text='Some reply comment.')
        reply3 = n.add_reply(user=create_user(), text='Some reply comment.')
        reply4 = n.add_reply(user=create_user(), text='Some reply comment.')

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

        reply1 = n.add_reply(user=create_user(), text='Some reply comment.')
        reply2 = n.add_reply(user=create_user(), text='Some reply comment.')
        reply3 = n.add_reply(user=create_user(), text='Some reply comment.')
        reply4 = n.add_reply(user=create_user(), text='Some reply comment.')

        n.delete_reply(reply_id=reply3.id)

        replies = list(n.get_replies())

        self.assertEqual(len(replies), 3)
        self.assertTrue(reply1 in replies)
        self.assertTrue(reply2 in replies)
        self.assertTrue(reply4 in replies)

    def test_reply_to_reply(self):
        """Test replying to a reply."""
        n = Notification.objects.create(created_user=self.user,
                                        text='Hello world',
                                        about=create_user(),
                                        source=NotificationSource.COMMENT)

        reply1 = n.add_reply(user=create_user(), text='Some reply comment.')
        reply2 = n.add_reply(user=create_user(),
                             reply_to=reply1,
                             text='Some reply comment.')

        replies = list(n.get_replies())

        self.assertEqual(len(replies), 2)
        self.assertTrue(replies[1], reply2)
        self.assertTrue(replies[1].reply_to, reply1)

    def test_is_comment(self):
        """Test indicating if the notification is a comment."""
        n = Notification(source=NotificationSource.COMMENT)
        self.assertTrue(n.is_comment())
        self.assertFalse(n.is_activity())

    def test_is_activity(self):
        """Test indicating if the notification is a comment."""
        n = Notification(source=NotificationSource.ACTIVITY)
        self.assertTrue(n.is_activity())
        self.assertFalse(n.is_comment())


class NotificationExtensionTests(SingleUserTestCase):

    def test_method_added_to_notification_model(self):
        n = Notification.objects.create(created_user=self.user,
                                        text='Hello world',
                                        about=create_user(),
                                        source=NotificationSource.COMMENT)
        self.assertTrue(hasattr(n, 'my_test_method'))
        self.assertEqual(n.my_test_method(), 'worked')

    def test_model_manager_extended(self):
        self.assertTrue(hasattr(Notification.objects, 'my_new_manager_method'))
        self.assertEqual(Notification.objects.my_new_manager_method(), 'works')
