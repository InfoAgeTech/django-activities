from __future__ import unicode_literals

from django.utils.translation import ugettext as _


class EnumCheck():
    """Adds a method to check if the enumeration value is a valid value.  If
    it is, then this returns the value.
    """

    @classmethod
    def check(cls, str_check):
        """Checks to see if a string is a value enum value. If yes, return the
        enum value.  Otherwise, return None.
        """
        if not str_check:
            return None

        str_check = str_check.upper()

        for s in cls.CHOICES:
            if s[0] == str_check:
                return s[0]

        return None

    @classmethod
    def get_display(cls, val):
        """Gets the display, human readable version of the enum value."""
        if not val:
            return None

        val = val.upper()

        for s in cls.CHOICES:
            if s[0] == val:
                return s[1]

        return None


class Source(EnumCheck):
    """The activity source represents what generated the activity.

    * SYSTEM - some system update performed on an object (i.e. a field update)
    * USER - a user is the source
    """
    SYSTEM = 'SYSTEM'
    USER = 'USER'
    CHOICES = ((SYSTEM, _('System')),
               (USER, _('User')),
               )


class Action(EnumCheck):
    """The past tense action choices for a activity.

    * COMMENTED - a user comment
    * CREATED - a created action
    * DELETED - a delete action
    * UPDATED - an update action
    """
    COMMENTED = 'COMMENTED'
    CREATED = 'CREATED'
    DELETED = 'DELETED'
    UPDATED = 'UPDATED'
    CHOICES = ((COMMENTED, _('Commented')),
               (CREATED, _('Created')),
               (DELETED, _('Deleted')),
               (UPDATED, _('Updated'))
               )


class Privacy(object):
    """Privacy for a activity."""
    PUBLIC = 'PUBLIC'  # everyone can see
    PRIVATE = 'PRIVATE'  # only created user can see
    CUSTOM = 'CUSTOM'  # a custom set of object has visibility
    CHOICES = ((PUBLIC, _('Public - everyone can see')),
               (PRIVATE, _('Private - only created user can see')),
               (CUSTOM, _('Custom - users must be granted visibility')),
               )
