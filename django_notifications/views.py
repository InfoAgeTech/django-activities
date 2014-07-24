from __future__ import unicode_literals

from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.views.generic.base import TemplateView
from django.views.generic.edit import DeleteView
from django.views.generic.edit import FormView
from django.views.generic.edit import UpdateView
from django_core.views import LoginRequiredViewMixin
from django_core.views import PagingViewMixin
from django_notifications.mixins.views import NotificationReplySingleObjectViewMixin
from django_notifications.mixins.views import NotificationSingleObjectViewMixin

from .forms import NotificationDeleteForm
from .forms import NotificationEditForm
from .forms import NotificationReplyEditForm
from .mixins.views import NotificationContentTypeObjectViewMixin
from .mixins.views import NotificationFormView
from .mixins.views import NotificationsViewMixin
from .mixins.views import UserNotificationsViewMixin


class NotificationsView(LoginRequiredViewMixin, PagingViewMixin,
                        NotificationContentTypeObjectViewMixin,
                        NotificationsViewMixin, NotificationFormView):

    template_name = 'notifications/view_notifications.html'

    def get_notifications_about_object(self):
        return self.content_object

    def get_context_data(self, **kwargs):
        context = super(NotificationsView, self).get_context_data(**kwargs)
        context['content_type'] = self.content_type
        context['content_object'] = self.content_object
        return context


# TODO: Is this view app specific?
class NotificationsForUserView(LoginRequiredViewMixin, PagingViewMixin,
                               UserNotificationsViewMixin,
                               NotificationFormView):

    template_name = 'notifications/view_notifications.html'


class NotificationView(LoginRequiredViewMixin,
                       NotificationSingleObjectViewMixin,
                       TemplateView):

    template_name = 'notifications/view_notification.html'


class NotificationEditView(LoginRequiredViewMixin,
                           NotificationSingleObjectViewMixin,
                           UpdateView):
    template_name = 'notifications/edit_notification.html'
    form_class = NotificationEditForm

    def get_form_kwargs(self):
        kwargs = super(NotificationEditView, self).get_form_kwargs()
        kwargs['instance'] = self.notification
        return kwargs

    def form_valid(self, form):
        # Ensure that the created user doesn't change
        form.instance.created_user = self.notification.created_user
        form.instance.last_modified_user = self.request.user
        return super(NotificationEditView, self).form_valid(form)

    def get_success_url(self):
        return self.notification.get_absolute_url()


class NotificationDeleteView(LoginRequiredViewMixin,
                             NotificationSingleObjectViewMixin,
                             FormView):

    template_name = 'notifications/delete_notification.html'
    form_class = NotificationDeleteForm

    def form_valid(self, form):

        if (self.notification.is_comment() and
            self.notification.created_user == self.request.user):
            # The user created this comment.  They can delete it for all.
            self.notification.delete()
        else:
            # Isn't this users comment, but they don't want this comment
            # showing up in the feed.  Remove it.
            self.notification.for_objs.remove(self.request.user)

        if self.request.is_ajax():
            return HttpResponse('success', status=200)

        return super(NotificationDeleteView, self).form_valid(form)

    def get_success_url(self):
        return self.notification.about.get_absolute_url()


class NotificationRepliesView(LoginRequiredViewMixin,
                              NotificationSingleObjectViewMixin,
                              TemplateView):
    template_name = 'notifications/view_notification_replies.html'


class NotificationReplyView(LoginRequiredViewMixin,
                            NotificationReplySingleObjectViewMixin,
                            TemplateView):
    template_name = 'notifications/view_notification_reply.html'


class NotificationReplyEditView(LoginRequiredViewMixin,
                           NotificationReplySingleObjectViewMixin,
                           UpdateView):
    template_name = 'notifications/edit_notification_reply.html'
    form_class = NotificationReplyEditForm

    def get_form_kwargs(self):
        kwargs = super(NotificationReplyEditView, self).get_form_kwargs()
        kwargs['instance'] = self.notification_reply
        return kwargs

    def form_valid(self, form):
        # Ensure that the created user doesn't change
        form.instance.created_user = self.notification_reply.created_user
        form.instance.last_modified_user = self.request.user
        return super(NotificationReplyEditView, self).form_valid(form)

    def get_success_url(self):
        return reverse('notification_reply_edit',
                       args=[self.notification.id, self.notification_reply.id])


class NotificationReplyDeleteView(LoginRequiredViewMixin,
                                  NotificationReplySingleObjectViewMixin,
                                  DeleteView):

    template_name = 'notifications/delete_notification_reply.html'

    def get_success_url(self):
        return self.notification.about.get_absolute_url()
