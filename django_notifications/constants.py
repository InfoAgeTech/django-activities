# -*- coding: utf-8 -*-

class NotificationSource():
    """The notification source represents what generated the notification

    comment - a user comment
    activity - this is some activity performed on a document (i.e. a field
        update)
    """
    COMMENT = 'COMMENT'
    ACTIVITY = 'ACTIVITY'
    CHOICES = ((COMMENT, 'Comment'),
               (ACTIVITY, 'Activity'))

    @classmethod
    def check(cls, source):
        """Checks to see if a notification source string is an actual source.
        If yes, return the notification source.  Otherwise, return None.
        """
        if not source:
            return None

        source = source.lower()

        for s in (cls.COMMENT, cls.ACTIVITY):
            if s == source:
                return s

        return None
