# -*- coding: utf-8 -*-
from django.contrib.auth import get_user_model
from django.db import models
from django.test import TestCase
from django_notifications.models import Notification
import uuid
from django_notifications.constants import NotificationSource

User = get_user_model()
random_string = lambda len = None: uuid.uuid4().hex[:len or 10]


def create_user(username=None, email=None):
    if not username:
        username = random_string()

    if not email:
        email = '{0}@{1}.com'.format(random_string(), random_string())

    return User.objects.create_user(username=username,
                                    email=email)

class NotificationTests(TestCase):

    @classmethod
    def setUpClass(cls):
        """Run once per test case"""
        super(NotificationTests, cls).setUpClass()
        cls.user = create_user()

    def setUp(self):
        """Run once per test."""
#        self.about_doc = MockDoc()
        pass

    def test_add_notification(self):
        """
        Testing adding notifications for a user.
        """
        text = 'Hello world'
        about_obj = create_user()

        n = Notification.add(created_user=self.user,
                             text=text,
                             about=about_obj,
                             source=NotificationSource.COMMENT)
        raise NotImplementedError()

#        n = Notification.add(created_user=self.usr,
#                             text=notification_text,
#                             doc=self.about_doc,
#                             source=NotificationSource.ACTIVITY)
#        self.assertEquals(n.text, notification_text)
#        self.assertEquals(n.doc.id, self.about_doc.id)
#        self.assertEquals(n.doc_id, self.about_doc.id)
#        self.assertEquals(n.source, NotificationSource.ACTIVITY)
#
#        self.assertTrue(self.usr in n.related_docs)
#        self.assertTrue(self.about_doc in n.related_docs)


#    def test_ensure_related_docs(self):
#        """Tests the ensure related docs functionality making sure specific
#        docs receive this notification."""
#        mockdoc_1 = MockDoc()
#        mockdoc_2 = MockDoc()
#        mockdoc_3 = MockDoc()
#
#        n = Notification.add(created_user=self.usr,
#                             text='Hello world',
#                             doc=self.about_doc,
#                             ensure_related_docs=[mockdoc_1,
#                                                  mockdoc_2,
#                                                  mockdoc_3],
#                             source=NotificationSource.ACTIVITY)
#        self.assertEquals(len(n.related_docs), 5)
#        self.assertTrue(self.usr in n.related_docs)
#        self.assertTrue(self.about_doc in n.related_docs)
#        self.assertTrue(mockdoc_1 in n.related_docs)
#        self.assertTrue(mockdoc_2 in n.related_docs)
#        self.assertTrue(mockdoc_3 in n.related_docs)
#
#
#    def test_delete_notification(self):
#        """Test verifying notification was successfully delete."""
#        n = Notification.add(created_user=self.usr,
#                             text='Hello world',
#                             doc=self.about_doc,
#                             source=NotificationSource.ACTIVITY)
#        notification = Notification.get_by_id(n.id)
#
#        self.assertEquals(notification.id, n.id)
#        n.delete()
#
#        notification = Notification.get_by_id(n.id)
#        self.assertIsNone(notification)
#
#
#    def test_add_notification_reply(self):
#        """Test verfiying you can correctly add a reply to a notification"""
#        n = Notification.add(created_user=self.usr,
#                             text='Hello world',
#                             doc=self.about_doc,
#                             source=NotificationSource.ACTIVITY)
#        self.assertEquals(len(n.replies), 0)
#
#        reply_text = 'This is awesome!'
#        n.add_reply(usr=self.usr, text=reply_text)
#
#        self.assertEquals(len(n.replies), 1)
#
#        n2 = Notification.get_by_id(id=n.id)
#
#        reply = n2.replies[0]
#        self.assertEquals(reply.text, reply_text)
#        self.assertEquals(reply.created, self.usr)
#
#    def test_get_reply_by_id(self):
#        """Test for getting a reply by id."""
#        n = Notification.add(created_user=self.usr,
#                             text='Hello world',
#                             doc=self.about_doc,
#                             source=NotificationSource.ACTIVITY)
#        self.assertEquals(len(n.replies), 0)
#
#        reply_text = 'This is awesome!'
#        n.add_reply(usr=self.usr, text='My first reply.')
#        n.add_reply(usr=self.usr, text='My second reply.')
#        reply_check = n.add_reply(usr=self.usr, text=reply_text)
#        n.add_reply(usr=self.usr, text='My fourth reply.')
#        reply_id_check = n.add_reply(usr=self.usr, text='My fifth reply.',
#                                     reply_to_id=reply_check.id)
#
#        reply_actual = n.get_reply_by_id(reply_id=reply_check.id)
#        self.assertEquals(reply_actual.id, reply_check.id)
#        self.assertEquals(reply_id_check.reply_to_id, reply_check.id)
#
#
#    def test_delete_notification_reply(self):
#        """Test for deleting a reply to a notification."""
#        n = Notification.add(created_user=self.usr,
#                             text='Hello world',
#                             doc=self.about_doc,
#                             source=NotificationSource.ACTIVITY)
#
#        reply_text_1 = 'This is awesome 1!'
#        reply_1 = n.add_reply(usr=self.usr, text=reply_text_1)
#
#        reply_text_2 = 'This is awesome 2!'
#        reply_2 = n.add_reply(usr=self.usr, text=reply_text_2)
#
#        self.assertEquals(len(n.replies), 2)
#        self.assertEquals(reply_2.id, n.replies[1].id)
#
#        n.delete_reply(reply_id=reply_2.id)
#
#        self.assertEquals(len(n.replies), 1)
#        self.assertEquals(reply_1.id, n.replies[0].id)
#
#
#    def test_get_by_doc(self):
#        """Test for getting a notification for a speific doc."""
#        doc_2 = MockDoc()
#        usr_2 = User.objects.create(id=random_alphanum_id())
#
#        Notification.add(created_user=self.usr,
#                         text='My first activity',
#                         doc=doc_2,
#                         source=NotificationSource.ACTIVITY)
#
#        Notification.add(created_user=self.usr,
#                         text='This is some comment.',
#                         doc=doc_2,
#                         source=NotificationSource.COMMENT)
#
#        Notification.add(created_user=self.usr,
#                         text='My second activity',
#                         doc=doc_2,
#                         source=NotificationSource.ACTIVITY)
#
#        Notification.add(created_user=usr_2,
#                         text='User 2s first activity',
#                         doc=doc_2,
#                         source=NotificationSource.ACTIVITY)
#
#        Notification.add(created_user=self.usr,
#                         text='My second comment',
#                         doc=doc_2,
#                         source=NotificationSource.COMMENT)
#
#        notifications = Notification.get_by_doc(doc=doc_2)[0]
#        self.assertEquals(len(notifications), 5)
#
#        notifications = Notification.get_by_doc(doc=doc_2,
#                                                source=NotificationSource.ACTIVITY)[0]
#        self.assertEquals(len(notifications), 3)
#
#        notifications = Notification.get_by_doc(doc=doc_2,
#                                                source=NotificationSource.COMMENT)[0]
#        self.assertEquals(len(notifications), 2)
#
#
#    def test_get_by_user(self):
#        """Test for getting notifications by a specific user."""
#        doc_2 = MockDoc()
#        usr_1 = User.objects.create(id=random_alphanum_id())
#        usr_2 = User.objects.create(id=random_alphanum_id())
#
#        Notification.add(created_user=usr_1,
#                         text='My first activity',
#                         doc=doc_2,
#                         source=NotificationSource.ACTIVITY)
#
#        Notification.add(created_user=usr_1,
#                         text='This is some comment.',
#                         doc=doc_2,
#                         source=NotificationSource.COMMENT)
#
#        Notification.add(created_user=usr_1,
#                         text='My second activity',
#                         doc=doc_2,
#                         source=NotificationSource.ACTIVITY)
#
#        Notification.add(created_user=usr_2,
#                         text='User 2s first activity',
#                         doc=doc_2,
#                         source=NotificationSource.ACTIVITY)
#
#        Notification.add(created_user=usr_1,
#                         text='My second comment',
#                         doc=doc_2,
#                         source=NotificationSource.COMMENT)
#
#        Notification.add(created_user=usr_2,
#                         text='User 2s first comment',
#                         doc=doc_2,
#                         source=NotificationSource.COMMENT)
#
#
#        notifications = Notification.get_by_user(usr=usr_1)[0]
#        self.assertEquals(len(notifications), 4)
#
#        notifications = Notification.get_by_user(usr=usr_1,
#                                                 source=NotificationSource.ACTIVITY)[0]
#        self.assertEquals(len(notifications), 2)
#
#        notifications = Notification.get_by_user(usr=usr_1,
#                                                 source=NotificationSource.COMMENT)[0]
#        self.assertEquals(len(notifications), 2)
#
#        notifications = Notification.get_by_user(usr=usr_2)[0]
#        self.assertEquals(len(notifications), 2)
#
#        notifications = Notification.get_by_user(usr=usr_2,
#                                                 source=NotificationSource.ACTIVITY)[0]
#        self.assertEquals(len(notifications), 1)
#
#        notifications = Notification.get_by_user(usr=usr_2,
#                                                 source=NotificationSource.COMMENT)[0]
#        self.assertEquals(len(notifications), 1)
