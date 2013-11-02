# -*- coding: utf-8 -*-
from django.core.paginator import EmptyPage
from django.core.paginator import Paginator

from ..constants import NotificationSource
from django_notifications import get_notification_model

Notification = get_notification_model()


class NotificationsViewMixin(object):
    """Notifications view mixin that returns the notification_obj's paginator
    and current page.

    Filtering
    =========
    You can further filter the notifications by passing the following query
    string params:

    * ns: notification source.  Can be one of .contants.NotificationSource.

    Note: This mixin requires the django_core.mixins.paging.PagingViewMixin
    to be called before this view is called.
    """

    def get_context_data(self, **kwargs):
        context = super(NotificationsViewMixin, self).get_context_data(**kwargs)

        notifications_about_object = self.get_notifications_about_object()
        notification_kwargs = {'obj': notifications_about_object}
        notification_source = NotificationSource.check(
                                                    self.request.GET.get('ns'))

        if notification_source:
            notification_kwargs['source'] = notification_source

        notifications = (Notification.objects
                           .get_for_object(**notification_kwargs)
                           .prefetch_related('about',
                                             'replies',
                                             'replies__created_user',
                                             'created_user'))

        paginator = Paginator(notifications, self.page_size)
        context['notifications_paginator'] = paginator

        try:
            context['notifications_page'] = paginator.page(self.page_num)
        except EmptyPage:
            context['notifications_page'] = paginator.page(paginator.num_pages)

        context['notifications_about_object'] = notifications_about_object
        return context

    def get_notifications_about_object(self):
        """Gets the object to get notifications for. The default is to return
        self.object which will be set if using a DetailView.  Otherwise, the
        consuming View can override this method.
        """
        if hasattr(self, 'object') and self.object != None:
            return self.object

        return self.get_object()
