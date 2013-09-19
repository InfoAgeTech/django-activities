# -*- coding: utf-8 -*-
from .models import Notification
from django.core.paginator import EmptyPage
from django.core.paginator import Paginator


class NotificationViewMixin(object):
    """Notifications view mixin that returns the notification_obj's paginator
    and current page.

    Note: This mixin requires the django_core.mixins.paging.PagingViewMixin
    to be called before this view is called.
    """
    notifications_about_object = None
    # notification_page_size_default = 15

    def get_context_data(self, **kwargs):
        context = super(NotificationViewMixin, self).get_context_data(**kwargs)
        # TODO: Might want to prefetch all the notification replies as well
        notifications = (Notification.objects
                           .get_for_object(obj=self.notifications_about_object)
                           .prefetch_related('about'))

        paginator = Paginator(notifications, self.page_size)
        context['notifications_paginator'] = paginator

        try:
            context['notifications_page'] = paginator.page(self.page_num)
        except EmptyPage:
            context['notifications_page'] = paginator.page(paginator.num_pages)

        return context
