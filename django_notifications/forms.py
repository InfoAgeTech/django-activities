from __future__ import unicode_literals

from django import forms
from django_core.forms.widgets import ReadonlyWidget
from django_core.forms.fields import CharFieldStripped
from django_notifications.models import Notification
from django_notifications.models import NotificationReply


class BasicCommentForm(forms.Form):
    """Basic form for commenting."""

    text = CharFieldStripped(max_length=500, widget=forms.Textarea())
    # Parent id of the comment or notification
    pid = forms.IntegerField(required=False, widget=forms.HiddenInput())
    next = CharFieldStripped(max_length=999999, required=False)


class BaseNotificationEditForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(BaseNotificationEditForm, self).__init__(*args, **kwargs)

        self.fields['created_user'].label = 'Created by'
        self.fields['created_user'].widget.attrs['value'] = \
            self.instance.created_user.get_full_name()
        self.fields['created_dttm'].label = 'Created'
        self.fields['created_dttm'].widget.attrs['readonly'] = 'readonly'
        self.fields['last_modified_user'].label = 'Last Modified by'
        self.fields['last_modified_user'].widget.attrs['value'] = \
            self.instance.last_modified_user.get_full_name()
        self.fields['last_modified_dttm'].label = 'Last Modified'
        self.fields['last_modified_dttm'].widget.attrs['readonly'] = 'readonly'

    def clean_created_dttm(self):
        return self.instance.created_dttm

    def clean(self):
        cleaned_data = super(BaseNotificationEditForm, self).clean()
        # Ignore errors for created user and last_modified_user since they are
        # readonly and can't be changed.
        cleaned_data['created_user'] = self.instance.created_user
        cleaned_data['last_modified_user'] = self.instance.last_modified_user

        if 'created_user' in self._errors:
            del self._errors['created_user']

        if 'last_modified_user' in self._errors:
            del self._errors['last_modified_user']

        return cleaned_data


class NotificationEditForm(BaseNotificationEditForm):

    class Meta:
        model = Notification
        fields = ['created_user', 'created_dttm', 'last_modified_user',
                  'last_modified_dttm', 'text']
        widgets = {
            'created_user': ReadonlyWidget(),
            'last_modified_user': ReadonlyWidget()
        }


class NotificationReplyEditForm(BaseNotificationEditForm):

    class Meta:
        model = NotificationReply
        fields = ['created_user', 'created_dttm', 'last_modified_user',
                  'last_modified_dttm', 'text']
        widgets = {
            'created_user': ReadonlyWidget(),
            'last_modified_user': ReadonlyWidget()
        }


class NotificationDeleteForm(forms.Form):
    """Form for deleting a notification."""
