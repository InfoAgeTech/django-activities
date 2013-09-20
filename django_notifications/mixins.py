# -*- coding: utf-8 -*-
from django.core.paginator import EmptyPage
from django.core.paginator import Paginator

from .constants import NotificationSource
from .models import Notification


class NotificationViewMixin(object):
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
    notifications_about_object = None
    # notification_page_size_default = 15

    def get_context_data(self, **kwargs):
        context = super(NotificationViewMixin, self).get_context_data(**kwargs)

        notification_kwargs = {'obj': self.notifications_about_object}
        notification_source = NotificationSource.check(
                                                    self.request.GET.get('ns'))

        if notification_source:
            notification_kwargs['source'] = notification_source

        notifications = (Notification.objects
                           .get_for_object(**notification_kwargs)
                           .prefetch_related('about',
                                             'replies',
                                             'created_user'))

        paginator = Paginator(notifications, self.page_size)
        context['notifications_paginator'] = paginator

        try:
            context['notifications_page'] = paginator.page(self.page_num)
        except EmptyPage:
            context['notifications_page'] = paginator.page(paginator.num_pages)

        context['notifications_about_object'] = self.notifications_about_object
        return context
