from __future__ import unicode_literals

from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.utils.translation import ugettext_lazy as _
from django.views.generic.base import TemplateView
from django.views.generic.edit import DeleteView
from django.views.generic.edit import FormView
from django.views.generic.edit import UpdateView
from django_core.views import PagingViewMixin
from django_core.views.mixins.generic import GenericObjectViewMixin

from .forms import ActivityDeleteForm
from .forms import ActivityEditForm
from .forms import ActivityReplyEditForm
from .mixins.views import ActivitiesViewMixin
from .mixins.views import ActivityCreatedUserRequiredViewMixin
from .mixins.views import ActivityFormView
from .mixins.views import ActivityReplySingleObjectViewMixin
from .mixins.views import ActivitySingleObjectViewMixin
from .mixins.views import UserActivitiesViewMixin


class ActivitiesView(PagingViewMixin, ActivitiesViewMixin, ActivityFormView):

    template_name = 'activities/view_activities.html'


class ActivitiesGenericObjectView(GenericObjectViewMixin, ActivitiesView):

    def get_activities_about_object(self):
        return self.content_object

    # TODO: this would no longer work for the current configuration
    def get_content_object_url(self):
        return reverse('activities_view', args=[self.content_type.id,
                                                self.content_object.id])


# TODO: Is this view app specific?
class ActivitiesForUserView(PagingViewMixin, UserActivitiesViewMixin,
                            ActivityFormView):

    template_name = 'activities/view_activities.html'


class ActivityView(ActivitySingleObjectViewMixin, TemplateView):

    template_name = 'activities/view_activity.html'


class ActivityEditView(ActivityCreatedUserRequiredViewMixin,
                       ActivitySingleObjectViewMixin, UpdateView):
    template_name = 'activities/edit_activity.html'
    form_class = ActivityEditForm

    def get_form_kwargs(self):
        kwargs = super(ActivityEditView, self).get_form_kwargs()
        kwargs['instance'] = self.activity
        kwargs['user'] = self.request.user
        return kwargs

    def get_success_url(self):
        return self.activity.get_absolute_url()


class ActivityDeleteView(ActivityCreatedUserRequiredViewMixin,
                         ActivitySingleObjectViewMixin, FormView):

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


class ActivityRepliesView(ActivitySingleObjectViewMixin, TemplateView):
    template_name = 'activities/view_activity_replies.html'


class ActivityReplyView(ActivityReplySingleObjectViewMixin, TemplateView):
    template_name = 'activities/view_activity_reply.html'


class ActivityReplyEditView(ActivityCreatedUserRequiredViewMixin,
                            ActivityReplySingleObjectViewMixin, UpdateView):
    template_name = 'activities/edit_activity_reply.html'
    form_class = ActivityReplyEditForm

    def get_form_kwargs(self):
        kwargs = super(ActivityReplyEditView, self).get_form_kwargs()
        kwargs['instance'] = self.activity_reply
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        messages.success(request=self.request,
                         message=_('Reply successfully updated!'),
                         fail_silently=True)
        return super(ActivityReplyEditView, self).form_valid(form)

    def get_success_url(self):
        return self.request.path


class ActivityReplyDeleteView(ActivityCreatedUserRequiredViewMixin,
                              ActivityReplySingleObjectViewMixin, DeleteView):

    template_name = 'activities/delete_activity_reply.html'

    def get_success_url(self):
        return self.activity.about.get_absolute_url()
