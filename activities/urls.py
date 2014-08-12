from __future__ import unicode_literals

from django.conf.urls import patterns
from django.conf.urls import url

from .views import ActivitiesView
from .views import ActivityDeleteView
from .views import ActivityEditView
from .views import ActivityRepliesView
from .views import ActivityReplyDeleteView
from .views import ActivityReplyEditView
from .views import ActivityReplyView
from .views import ActivityView


urlpatterns = patterns('',
    url(r'^/(?P<content_type_id>\d+)/(?P<object_id>\d+)/?$', ActivitiesView.as_view(), name='activities_view'),
    url(r'^/(?P<activity_id>\d+)/delete/?$', ActivityDeleteView.as_view(), name='activity_delete'),
    url(r'^/(?P<activity_id>\d+)/edit/?$', ActivityEditView.as_view(), name='activity_edit'),
    url(r'^/(?P<activity_id>\d+)/replies/(?P<reply_id>\d+)/delete/?$', ActivityReplyDeleteView.as_view(), name='activity_reply_delete'),
    url(r'^/(?P<activity_id>\d+)/replies/(?P<reply_id>\d+)/edit/?$', ActivityReplyEditView.as_view(), name='activity_reply_edit'),
    url(r'^/(?P<activity_id>\d+)/replies/(?P<reply_id>\d+)/?$', ActivityReplyView.as_view(), name='activity_reply'),
    url(r'^/(?P<activity_id>\d+)/replies/?$', ActivityRepliesView.as_view(), name='activity_replies'),
    url(r'^/(?P<activity_id>\d+)/?$', ActivityView.as_view(), name='activity_view'),
)
