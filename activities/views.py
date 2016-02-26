from datetime import datetime

from activities.mixins.views import ActivityViewMixin
from activities.models import ActivityReply
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.utils.translation import ugettext_lazy as _
from django.views.generic.base import TemplateView
from django.views.generic.edit import DeleteView
from django.views.generic.edit import FormView
from django.views.generic.edit import UpdateView
from django.views.generic.list import ListView
from django_core.utils.urls import build_url
from django_core.views import PagingViewMixin
from django_core.views.mixins.ajax import AjaxViewMixin
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

    def get_context_data(self, *args, **kwargs):
        context = super(ActivitiesView, self).get_context_data(*args, **kwargs)
        context['is_view_activities_page'] = True
        return context


class ActivitiesGenericObjectView(GenericObjectViewMixin, ActivitiesView):

    def get_activities_about_object(self):
        return self.content_object

    # TODO: this would no longer work for the current configuration
    def get_content_object_url(self):
        url_args = [self.generic_object_content_type.id,
                    self.content_object.id]
        return reverse('activities_view', args=url_args)


# TODO: Is this view app specific?
class ActivitiesForUserView(PagingViewMixin, UserActivitiesViewMixin,
                            ActivityFormView):
    template_name = 'activities/view_activities.html'


class ActivityView(PagingViewMixin, ActivityViewMixin, AjaxViewMixin, ListView):
    """View for an activity.  The paging is for the activity replies.

    Querystring params:

    - ts: timestamp to ensure all replies are less than this value.  This helps
        prevent duplicates show up in paging if new replies are added between
        user paging.
    """
    template_name = 'activities/view_activity.html'
    ajax_template_name = 'activities/snippets/activity_replies.html'
    model = ActivityReply
    context_object_name = 'activity_replies'

    def get_context_data(self, **kwargs):
        context = super(ActivityView, self).get_context_data(**kwargs)
        has_more = context['page_obj'].has_next()
        context['activity_replies_has_more'] = has_more

        if has_more:
            querystring_params = {
                'p': self.page_num + 1,
                'ps': self.page_size
            }

            dt = self.get_query_timestamp_datetime()

            if not dt and self.page_num == 1:
                # it's the first page so add the timestamp to the url
                dt = datetime.utcnow()

            if dt:
                querystring_params['ts'] = dt.timestamp()

            context['activity_replies_next_url'] = build_url(
                url=self.activity.get_absolute_url(),
                querystring_params=querystring_params
            )

        return context

    def get_queryset(self, **kwargs):
        queryset = super(ActivityView, self).get_queryset(**kwargs)
        filter_kwargs = {
            'activity': self.activity
        }

        dt = self.get_query_timestamp_datetime()

        if dt:
            filter_kwargs['created_dttm__lte'] = dt

        return queryset.filter(
            **filter_kwargs
        ).order_by('-created_dttm').prefetch_related('activity', 'created_user')

    def get_query_timestamp_datetime(self):
        """Gets the timestamp from the url and converts it to a datetime."""
        try:
            timestamp = float(self.request.GET.get('ts'))
            return datetime.fromtimestamp(timestamp)
        except:
            return None


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

        if self.activity.created_user == self.request.user:
            # The user created this comment.  They can delete it for all.
            self.activity.delete()
        else:
            # Isn't this users comment, but they don't want this comment
            # showing up in the feed.  Remove it.
            activity_for = self.activity.for_objs.get_for_object(
                obj=self.request.user
            ).first()

            if activity_for:
                self.activity.for_objs.remove(activity_for)

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
