from __future__ import unicode_literals

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _
from django_core.forms.fields import CharFieldStripped
from django_core.forms.mixins.users import UserFormMixin
from django_core.forms.widgets import ReadonlyWidget

from .models import Notification
from .models import NotificationReply


class BasicCommentForm(forms.Form):
    """Basic form for commenting."""

    text = CharFieldStripped(max_length=500, widget=forms.Textarea())
    # Parent id of the comment or notification
    pid = forms.IntegerField(required=False, widget=forms.HiddenInput())
    next = CharFieldStripped(max_length=999999, required=False)


class BaseNotificationEditForm(UserFormMixin, forms.ModelForm):

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

    def clean_created_user(self):
        return self.instance.created_user

    def clean_last_modified_user(self):

        if not self.user.is_authenticated():
            raise ValidationError(_('User must be logged in.'))

        return self.user


class NotificationEditForm(BaseNotificationEditForm):

    class Meta:
        model = Notification
        fields = ('created_user', 'created_dttm', 'last_modified_user',
                  'last_modified_dttm', 'text')
        widgets = {
            'created_user': ReadonlyWidget(),
            'last_modified_user': ReadonlyWidget()
        }


class NotificationReplyEditForm(BaseNotificationEditForm):

    class Meta:
        model = NotificationReply
        fields = ('created_user', 'created_dttm', 'last_modified_user',
                  'last_modified_dttm', 'text')
        widgets = {
            'created_user': ReadonlyWidget(),
            'last_modified_user': ReadonlyWidget()
        }


class NotificationDeleteForm(forms.Form):
    """Form for deleting a notification."""
