# -*- coding: utf-8 -*-
from django.core.paginator import EmptyPage
from django.core.paginator import Paginator

from ..constants import NotificationSource
from django_notifications import get_notification_model
from django.views.generic.detail import SingleObjectMixin
from django_notifications.models import NotificationReply

Notification = get_notification_model()


class NotificationViewMixin(object):
    """View mixin for a single notification object."""

    notification = None
    notification_pk_url_kwarg = 'notification_id'

    def dispatch(self, *args, **kwargs):
        self.notification = self.get_notification(**kwargs)
        return super(NotificationViewMixin, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(NotificationViewMixin, self).get_context_data(**kwargs)
        context['notification'] = self.notification
        return context

    def get_notification(self, **kwargs):
        if self.notification:
            return self.notification

        self.notification = Notification.objects.get_by_id_or_404(
                                id=kwargs.get(self.notification_pk_url_kwarg))
        return self.notification


class NotificationSingleObjectViewMixin(NotificationViewMixin,
                                        SingleObjectMixin):
    """Mixin for when the notification represents what the page is about."""

    def dispatch(self, *args, **kwargs):
        self.object = self.get_notification(**kwargs)
        return super(NotificationSingleObjectViewMixin,
                     self).dispatch(*args, **kwargs)

    def get_object(self, **kwargs):
        return self.notification


class NotificationReplyViewMixin(NotificationViewMixin):
    """View mixin for a notification reply."""

    notification_reply = None
    notification_reply_pk_url_kwarg = 'reply_id'

    def dispatch(self, *args, **kwargs):
        self.notification_reply = self.get_notification_reply(**kwargs)
        # I do this do the correct notification proxy model is used.
        self.notification_reply.notification = self.get_notification(**kwargs)
        return super(NotificationReplyViewMixin,
                     self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(NotificationReplyViewMixin,
                        self).get_context_data(**kwargs)
        context['notification_reply'] = self.notification_reply
        return context

    def get_notification_reply(self, **kwargs):
        if self.notification_reply:
            return self.notification_reply

        self.notification_reply = NotificationReply.objects.get_by_id_or_404(
                        id=kwargs.get(self.notification_reply_pk_url_kwarg),
                        select_related=True)
        return self.notification_reply


class NotificationReplySingleObjectViewMixin(NotificationReplyViewMixin,
                                             SingleObjectMixin):
    """Mixin for when the notification reply represents what the page is about.
    """

    def dispatch(self, *args, **kwargs):
        self.object = self.get_notification_reply(**kwargs)
        return super(NotificationReplySingleObjectViewMixin,
                     self).dispatch(*args, **kwargs)

    def get_object(self, **kwargs):
        return self.notification_reply


class NotificationsViewMixin(object):
    """Notifications view mixin that returns the notification_obj's paginator
    and current page the the authenticated user is able to see.

    Filtering
    =========
    You can further filter the notifications by passing the following query
    string params:

    * ns: notification source.  Can be one of .contants.NotificationSource.

    Note: This mixin requires the django_core.mixins.paging.PagingViewMixin
    to be called before this view is called.
    """
    notifications_page_num = 1
    notifications_page_size = 15
    notifications_paginate_by = notifications_page_size
    notifications_page_kwarg = 'np'
    notifications_page_size_kwarg = 'nps'

    def dispatch(self, *args, **kwargs):

        if self.notifications_page_size != self.notifications_paginate_by:
            # Default to the paginate_by value if these two if different.
            self.notifications_page_size = self.notifications_paginate_by

        self.notifications_page_num, self.notifications_page_size = \
            self.get_notifications_paging()
        self.notifications_paginate_by = self.notifications_page_size
        return super(NotificationsViewMixin, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(NotificationsViewMixin,
                        self).get_context_data(**kwargs)

        notifications = self.get_notifications_queryset()

        paginator = Paginator(notifications, self.notifications_page_size)
        context['notifications_paginator'] = paginator

        try:
            context['notifications_page'] = \
                paginator.page(self.notifications_page_num)
        except EmptyPage:
            context['notifications_page'] = paginator.page(paginator.num_pages)

        context['notifications_about_object'] = \
            self.get_notifications_about_object()

        return context

    def get_notifications_queryset(self):
        """Get's the queryset for the notifications."""
        notifications_about_object = self.get_notifications_about_object()

        notification_kwargs = {'for_user': self.request.user}

        if notifications_about_object:
            notification_kwargs['obj'] = notifications_about_object

        notification_source = NotificationSource.check(
                                                    self.request.GET.get('ns'))

        if notification_source:
            notification_kwargs['source'] = notification_source

        return (Notification.objects.get_for_object(**notification_kwargs)
                                    .prefetch_related('about',
                                                      'replies',
                                                      'replies__created_user',
                                                      'created_user'))

    def get_notifications_about_object(self):
        """Gets the object to get notifications for. The default is to return
        self.object which will be set if using a DetailView.  Otherwise, the
        consuming View can override this method.

        This can be a single object or a list, tuple or set of objects.
        """
        if hasattr(self, 'object') and self.object != None:
            return self.object

        return self.get_object()

    def get_notifications_paging(self):
        """Gets the paging values passed through the query string params.

            * "np" for "notifications page number" and
            * "nps" for "notifications page size".

        :returns: tuple with the page being the first part and the page size
            being the second part.
        """
        orig_page_num = self.notifications_page_num
        orig_page_size = self.notifications_page_size

        try:

            page_num = int(self.request.GET.get(self.notifications_page_kwarg))

            if page_num < 1:
                page_num = orig_page_num
        except:
            page_num = orig_page_num

        try:
            orig_page_size = self.notifications_page_size
            page_size = int(self.request.GET.get(
                                        self.notifications_page_size_kwarg))

            if page_size < 1:
                page_size = orig_page_size
        except:
            page_size = orig_page_size

        return page_num, page_size
