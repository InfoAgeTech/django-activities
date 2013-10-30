# -*- coding: utf-8 -*-


class NotificationSource():
    """The notification source represents what generated the notification


    ACTIVITY - this is some activity performed on an object (i.e. a field
        update)
    COMMENT - a user comment
    CREATED - represents an object being created
    DELETED - represents an object being deleted
    """
    ACTIVITY = 'ACTIVITY'
    COMMENT = 'COMMENT'
    CREATED = 'CREATED'
    DELETED = 'DELETED'
    CHOICES = ((ACTIVITY, 'Activity'),
               (CREATED, 'Created'),
               (COMMENT, 'Comment'),
               (DELETED, 'Deleted')
               )

    @classmethod
    def check(cls, source):
        """Checks to see if a notification source string is an actual source.
        If yes, return the notification source.  Otherwise, return None.
        """
        if not source:
            return None

        source = source.upper()

        for s in cls.CHOICES:
            if s[0] == source:
                return s[0]

        return None
