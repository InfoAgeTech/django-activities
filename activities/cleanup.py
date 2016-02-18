from logging import getLogger

from activities.models import Activity
from django.contrib.contenttypes.models import ContentType


logger = getLogger(__name__)


class ActivityCleaner(object):
    """The activity cleanup is a class that cleans up activities that don't have
    a valid "about" object.  This can happen if the "about" object is deleted
    and the notifications weren't cleaned up properly.

    >>> cleaner = ActivityCleaner()
    >>> cleaner.cleanup()
    """
    def get_distinct_content_type_ids(self):
        """Gets the distinct content type ids that exist in the db."""
        return (Activity.objects.order_by()
                                .values_list('about_content_type', flat=True)
                                .distinct())

    def get_about_ids_by_content_type(self, content_type):
        """Get about ids that exist in the db."""
        return (Activity.objects.filter(about_content_type=content_type,
                                        about_id__isnull=False)
                                .order_by()
                                .values_list('about_id', flat=True)
                                .distinct())

    def cleanup(self, is_dry_run=True):
        """Performs the cleanup of the the stale activities (activities that
        have no valid about object).

        :param is_dry_run: boolean indicating if the objects should be deleted
            from the database or not.  If False, this will only print out the
            ids of the items that would be cleaned up.
        """
        content_type_ids = self.get_distinct_content_type_ids()
        cleaned_about_ids = {}

        for content_type_id in content_type_ids:
            content_type = ContentType.objects.filter(id=content_type_id).first()

            if not content_type:
                continue

            model = content_type.model_class()
            unique_about_ids = self.get_about_ids_by_content_type(
                content_type=content_type
            )
            existing_about_ids = (model.objects.filter(id__in=unique_about_ids)
                                               .values_list('id', flat=True))

            # these are the ids of the objects that no longer exist in the db
            stale_about_ids = set(unique_about_ids).difference(existing_about_ids)

            if stale_about_ids:
                cleanup_queryset = Activity.objects.filter(
                    about_content_type=content_type,
                    about_id__in=stale_about_ids
                )
                logger.info(
                    'Cleaning up {0} activities for the following stale '
                    '"{1}" instance ids: {2}'.format(cleanup_queryset.count(),
                                                     model,
                                                     stale_about_ids))

                cleaned_about_ids[model] = list(stale_about_ids)

                if not is_dry_run:
                    cleanup_queryset.delete()

        return cleaned_about_ids
