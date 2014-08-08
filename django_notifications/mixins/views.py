from __future__ import unicode_literals

from django.contrib.contenttypes.models import ContentType
from django.core.paginator import EmptyPage
from django.core.paginator import Paginator
from django.core.urlresolvers import reverse
from django.http.response import Http404
from django.http.response import HttpResponse
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.edit import FormView

from .. import get_notification_model
from ..constants import Source
from ..forms import BasicCommentForm
from ..http import NotificationResponse
from ..models import NotificationReply
from django_notifications.constants import Action


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
            id=kwargs.get(self.notification_pk_url_kwarg)
        )
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
            select_related=True
        )
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

    Filtering:

    You can further filter the notifications by passing the following query
    string params:

    * ns: notification source.  Can be one of .contants.Source.

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

        if 'notification_url' not in context:
            context['notification_url'] = self.get_notification_url()

        return context

    def get_notifications_queryset(self):
        """Get's the queryset for the notifications."""
        notifications_about_object = self.get_notifications_about_object()
        notification_kwargs = {}

        if notifications_about_object:
            notification_kwargs['obj'] = notifications_about_object

        # TODO: need to validate this is correct since "action" was added to
        #       the model
        notification_source = Source.check(self.request.GET.get('ns'))

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
        if hasattr(self, 'object') and self.object is not None:
            return self.object

        return self.get_object()

    def get_notification_url(self):
        """Get the notification url for the notification object."""
        # TODO: Would be nice to try and optimize this so I don't have to query
        #       for the content type if possible.
        about_obj = self.get_notifications_about_object()
        content_type = ContentType.objects.get_for_model(about_obj)
        return reverse('notifications_view', args=[content_type.id,
                                                   about_obj.id])

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
                self.notifications_page_size_kwarg)
            )

            if page_size < 1:
                page_size = orig_page_size
        except:
            page_size = orig_page_size

        return page_num, page_size


class UserNotificationsViewMixin(NotificationsViewMixin):
    """Notifications for the authenticated user."""

    def get_notifications_about_object(self):
        return self.request.user


class NotificationFormView(FormView):
    """This is a form view that handles adding and displaying notifications
    for an object.

    This must be called after after any subclass of
    django_notifications.mixins.NotificationsViewMixin so this mixin has access
    to the `notifications_about_object` attribute.
    """
    form_class = BasicCommentForm

    def get(self, request, *args, **kwargs):
        # TODO: do I need to make an additional check here to make sure this is
        #       an ajax get request for notifications?
        if self.request.is_ajax():
            return render_to_response(
                'django_notifications/snippets/notifications.html',
                self.get_context_data(),
                context_instance=RequestContext(self.request)
            )

        return super(NotificationFormView, self).get(request=request,
                                                     *args,
                                                     **kwargs)

    def get_context_data(self, **kwargs):
        context = super(NotificationFormView, self).get_context_data(**kwargs)

        if self.request.is_ajax():
            context['obj'] = self.get_notifications_about_object()

        return context

    def form_valid(self, form):

        # TODO: Need to make sure the user has the ability to comment on this
        #       object (they are sharing or authorized to do so.  Also,
        #       probably want to require ajax here?
        text = form.cleaned_data.get('text').strip()

        # if "pid" (parent_notification_id) exists, then this is a reply to a
        # notification.
        parent_notification_id = form.cleaned_data.get('pid')

        if parent_notification_id:
            # reply to an existing notification
            notification = Notification.objects.get_by_id(
                id=parent_notification_id
            )

            if not notification:
                raise HttpResponse(status=400)

            notification.add_reply(user=self.request.user,
                                   text=text)

        else:
            # New notification for an object
            notification = Notification.objects.create(
                created_user=self.request.user,
                text=text,
                about=self.get_notifications_about_object(),
                source=Source.USER,
                action=Action.COMMENTED
            )

        if self.request.is_ajax():
            return NotificationResponse(request=self.request,
                                        notification=notification)

        # TODO: Where do I redirect to if it's not an ajax request?
        # return ''  # safe_redirect(self.request.POST.get('next') or '/')
        return super(NotificationFormView, self).form_valid(form=form)

    def form_invalid(self, form):
        # TODO: what do I want to do here?
        return super(NotificationFormView, self).form_invalid(form=form)


# TODO: This isn't Notifications specific and could be moved elsewhere.
class ContentTypeObjectViewMixin(object):
    """View mixin that takes the content type id and object id from the url
    and it gets the object it refers to.
    """
    def dispatch(self, *args, **kwargs):
        try:
            # TODO: Do I want to accept a content type id or name?
            content_type_id = kwargs['content_type_id']
            object_id = kwargs['object_id']
        except:
            raise Http404

        try:
            self.content_type = ContentType.objects.get_for_id(
                id=content_type_id
            )
        except:
            raise Http404

        content_model = self.content_type.model_class()

        try:
            self.content_object = content_model.objects.get(id=object_id)
        except:
            raise Http404

        return super(ContentTypeObjectViewMixin, self).dispatch(*args,
                                                                **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ContentTypeObjectViewMixin,
                        self).get_context_data(**kwargs)
        context['content_type'] = self.content_type
        context['content_object'] = self.content_object
        return context


class NotificationContentTypeObjectViewMixin(ContentTypeObjectViewMixin):
    """Notification content type mixin."""

    def get_context_data(self, **kwargs):
        context = super(NotificationContentTypeObjectViewMixin,
                        self).get_context_data(**kwargs)
        context['notification_url'] = reverse('notifications_view',
                                              args=[self.content_type.id,
                                                    self.content_object.id])
        return context
