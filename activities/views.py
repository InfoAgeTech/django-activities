from __future__ import unicode_literals

from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.views.generic.base import TemplateView
from django.views.generic.edit import DeleteView
from django.views.generic.edit import FormView
from django.views.generic.edit import UpdateView
from django_core.views import LoginRequiredViewMixin
from django_core.views import PagingViewMixin

from .forms import ActivityDeleteForm
from .forms import ActivityEditForm
from .forms import ActivityReplyEditForm
from .mixins.views import ActivitiesViewMixin
from .mixins.views import ActivityContentTypeObjectViewMixin
from .mixins.views import ActivityFormView
from .mixins.views import ActivityReplySingleObjectViewMixin
from .mixins.views import ActivitySingleObjectViewMixin
from .mixins.views import UserActivitiesViewMixin


class ActivitiesView(LoginRequiredViewMixin, PagingViewMixin,
                     ActivityContentTypeObjectViewMixin, ActivitiesViewMixin,
                     ActivityFormView):

    template_name = 'activities/view_activities.html'

    def get_activities_about_object(self):
        return self.content_object

    def get_context_data(self, **kwargs):
        context = super(ActivitiesView, self).get_context_data(**kwargs)
        context['content_type'] = self.content_type
        context['content_object'] = self.content_object
        return context


# TODO: Is this view app specific?
class ActivitiesForUserView(LoginRequiredViewMixin, PagingViewMixin,
                            UserActivitiesViewMixin, ActivityFormView):

    template_name = 'activities/view_activities.html'


class ActivityView(LoginRequiredViewMixin, ActivitySingleObjectViewMixin,
                   TemplateView):

    template_name = 'activities/view_activity.html'


class ActivityEditView(LoginRequiredViewMixin, ActivitySingleObjectViewMixin,
                       UpdateView):
    template_name = 'activities/edit_activity.html'
    form_class = ActivityEditForm

    def get_form_kwargs(self):
        kwargs = super(ActivityEditView, self).get_form_kwargs()
        kwargs['instance'] = self.activity
        kwargs['user'] = self.request.user
        return kwargs

    def get_success_url(self):
        return self.activity.get_absolute_url()


class ActivityDeleteView(LoginRequiredViewMixin, ActivitySingleObjectViewMixin,
                         FormView):

    template_name = 'activities/delete_activity.html'
    form_class = ActivityDeleteForm

    def form_valid(self, form):

        if self.activity.is_comment() and \
           self.activity.created_user == self.request.user:
            # The user created this comment.  They can delete it for all.
            self.activity.delete()
        else:
            # Isn't this users comment, but they don't want this comment
            # showing up in the feed.  Remove it.
            self.activity.for_objs.remove(self.request.user)

        if self.request.is_ajax():
            return HttpResponse('success', status=200)

        return super(ActivityDeleteView, self).form_valid(form)

    def get_success_url(self):
        return self.activity.about.get_absolute_url()


class ActivityRepliesView(LoginRequiredViewMixin,
                          ActivitySingleObjectViewMixin, TemplateView):
    template_name = 'activities/view_activity_replies.html'


class ActivityReplyView(LoginRequiredViewMixin,
                        ActivityReplySingleObjectViewMixin, TemplateView):
    template_name = 'activities/view_activity_reply.html'


class ActivityReplyEditView(LoginRequiredViewMixin,
                            ActivityReplySingleObjectViewMixin, UpdateView):
    template_name = 'activities/edit_activity_reply.html'
    form_class = ActivityReplyEditForm

    def get_form_kwargs(self):
        kwargs = super(ActivityReplyEditView, self).get_form_kwargs()
        kwargs['instance'] = self.activity_reply
        kwargs['user'] = self.request.user
        return kwargs

    def get_success_url(self):
        return reverse('activity_reply_edit',
                       args=[self.activity.id, self.activity_reply.id])


class ActivityReplyDeleteView(LoginRequiredViewMixin,
                              ActivityReplySingleObjectViewMixin, DeleteView):

    template_name = 'activities/delete_activity_reply.html'

    def get_success_url(self):
        return self.activity.about.get_absolute_url()
