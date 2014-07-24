from __future__ import unicode_literals

from django.conf.urls import patterns
from django.conf.urls import url

from .views import NotificationDeleteView
from .views import NotificationEditView
from .views import NotificationRepliesView
from .views import NotificationReplyDeleteView
from .views import NotificationReplyEditView
from .views import NotificationReplyView
from .views import NotificationView
# from .views import NotificationsForUserView
from .views import NotificationsView


urlpatterns = patterns('',
    # TODO: might need to remove the NotificationsForUserView?
    # url(r'^/?$', NotificationsForUserView.as_view(), name='notifications_view'),
    url(r'^/(?P<content_type_id>\d+)/(?P<object_id>\d+)/?$', NotificationsView.as_view(), name='notifications_view'),
    url(r'^/(?P<notification_id>\d+)/delete/?$', NotificationDeleteView.as_view(), name='notification_delete'),
    url(r'^/(?P<notification_id>\d+)/edit/?$', NotificationEditView.as_view(), name='notification_edit'),
    url(r'^/(?P<notification_id>\d+)/replies/(?P<reply_id>\d+)/delete/?$', NotificationReplyDeleteView.as_view(), name='notification_reply_delete'),
    url(r'^/(?P<notification_id>\d+)/replies/(?P<reply_id>\d+)/edit/?$', NotificationReplyEditView.as_view(), name='notification_reply_edit'),
    url(r'^/(?P<notification_id>\d+)/replies/(?P<reply_id>\d+)/?$', NotificationReplyView.as_view(), name='notification_reply'),
    url(r'^/(?P<notification_id>\d+)/replies/?$', NotificationRepliesView.as_view(), name='notification_replies'),
    url(r'^/(?P<notification_id>\d+)/?$', NotificationView.as_view(), name='notification_view'),
)
