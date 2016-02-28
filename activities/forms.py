from activities.constants import Action
from activities.constants import Source
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _
from django_core.forms.fields import CharFieldStripped
from django_core.forms.mixins.users import UserFormMixin
from django_core.forms.widgets import ReadonlyWidget

from .models import Activity
from .models import ActivityReply


ACTIVITY_ACTION_CHOICES = (
    (Action.COMMENTED, Action.COMMENTED),
    (Action.SHARED, Action.SHARED)
)


class ActivityActionForm(UserFormMixin, forms.Form):
    """Basic form for creating an action about an activity.

    Fields:

    - parent_activity: the parent activity.  If one exists, this is a a reply
        to that activity.
    """

    text = CharFieldStripped(max_length=500, widget=forms.Textarea(),
                             required=False)
    parent_activity = forms.ModelChoiceField(queryset=Activity.objects.all(),
                                             required=False,
                                             widget=forms.HiddenInput)
    next = CharFieldStripped(max_length=999999, required=False)
    action = forms.ChoiceField(choices=ACTIVITY_ACTION_CHOICES,
                               widget=forms.HiddenInput)

    def __init__(self, about, *args, **kwargs):
        """
        :param about: the object that this form is about.
        """
        super(ActivityActionForm, self).__init__(*args, **kwargs)
        self.about = about

    def clean(self, *args, **kwargs):
        cleaned_data = super(ActivityActionForm, self).clean(*args, **kwargs)

        text = cleaned_data.get('text')
        action = cleaned_data.get('action')

        if action == Action.COMMENTED and not text:
            # text field is required for comment actions
            self.add_error('text', _('This field is required.'))

        return cleaned_data

    def save(self, *args, **kwargs):
        """Saves a new Activity or ActivityReply depending on if the parent id
        exists in the form.
        """
        # TODO: Need to make sure the user has the ability to comment on this
        #       object (they are sharing or authorized to do so.  Also,
        #       probably want to require ajax here?
        text = self.cleaned_data.get('text')
        parent_activity = self.cleaned_data.get('parent_activity')
        action = self.cleaned_data.get('action')

        if not action and text:
            action = Action.COMMENTED

        if parent_activity:
            # reply to an existing activity
            return parent_activity.add_reply(user=self.user, text=text)

        if action == Action.SHARED:
            # if the object share already exists, then it needs to be removed
            # since an object can only be shared once per user

            activity = Activity.objects.get_about_object(
                action=Action.SHARED,
                created_user=self.user,
                about=self.about
            )

            if activity:
                # activity exists already.  So delete it since this works as a
                # toggle (share/remove share).
                activity.delete()
                return None

        ensure_for_objs = []
        about = self.about

        if about == self.user or action == Action.SHARED:
            # user commenting on own wall
            ensure_for_objs.append(self.user)

        # New activity for an object
        return Activity.objects.create(
            created_user=self.user,
            text=text,
            about=about,
            source=Source.USER,
            action=action,
            ensure_for_objs=ensure_for_objs or None
        )


class BaseActivityEditForm(UserFormMixin, forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(BaseActivityEditForm, self).__init__(*args, **kwargs)

        if 'created_user' in self.fields:
            self.fields['created_user'].label = 'Created by'
            self.fields['created_user'].widget.attrs['value'] = \
                self.instance.created_user.get_full_name()

        if 'created_dttm' in self.fields:
            self.fields['created_dttm'].label = 'Created'
            self.fields['created_dttm'].widget.attrs['readonly'] = 'readonly'

        if 'last_modified_user' in self.fields:
            self.fields['last_modified_user'].label = 'Last Modified by'
            self.fields['last_modified_user'].widget.attrs['value'] = \
                self.instance.last_modified_user.get_full_name()

        if 'last_modified_dttm' in self.fields:
            self.fields['last_modified_dttm'].label = 'Last Modified'
            self.fields['last_modified_dttm'].widget.attrs['readonly'] = 'readonly'

    def clean_created_dttm(self):
        return self.instance.created_dttm

    def clean_created_user(self):
        return self.instance.created_user

    def clean_last_modified_user(self):

        if not self.user.is_authenticated():
            raise ValidationError(_('User must be logged in.'))

        return self.user

    def clean(self, *args, **kwargs):
        cleaned_data = super(BaseActivityEditForm, self).clean(*args, **kwargs)

        # created user shouldn't error since it should always be the same
        if 'created_user' in self.errors:
            cleaned_data['created_user'] = self.instance.created_user
            del self.errors['created_user']

        if self.user.is_authenticated() and 'last_modified_user' in self.errors:
            cleaned_data['last_modified_user'] = self.user
            del self.errors['last_modified_user']

        return cleaned_data


class ActivityEditForm(BaseActivityEditForm):
    """Form for editing an activity."""

    class Meta:
        model = Activity
        fields = ('text',)

    def clean(self, **kwargs):
        cleaned_data = super(ActivityEditForm, self).clean(**kwargs)

        if self.instance.action != Action.COMMENTED:
            self.add_error(None, 'Only comments can be edited.')

        return cleaned_data


class ActivityReplyEditForm(BaseActivityEditForm):
    """Form for editing an activity reply."""

    class Meta:
        model = ActivityReply
        fields = ('text',)


class ActivityDeleteForm(forms.Form):
    """Form for deleting a activity."""
