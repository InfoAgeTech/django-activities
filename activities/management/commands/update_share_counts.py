from datetime import datetime
from logging import getLogger

from activities.constants import Action
from activities.models import Activity
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand


logger = getLogger(__name__)

class Command(BaseCommand):
    help = "Updates the share counts on objects that are shareable."

    def add_arguments(self, parser):
        parser.add_argument('-d', '--dry_run',
                            dest='dry_run',
                            default=False,
                            type=bool,
                            help=('boolean indicating if the images should '
                                  'actually be processed or if the function '
                                  'out just wants to be seen.'))

    def handle(self, dry_run=False, *args, **options):
        """
        :param dry_run: boolean indicating if the objects should actually be
            processed or if the function out just wants to be seen.
        """
        if dry_run == True:
            logger.info('"dry_run" has been set to true. No actual '
                         'updates will be made.')

        start = datetime.utcnow()

        # get all content types that have object shares
        content_types_with_shares = (Activity.objects.filter(
            action=Action.SHARED
        ).order_by('about_content_type').distinct(
            'about_content_type'
        ).values_list('about_content_type_id', flat=True))

        total_objects_updated = 0

        for content_type_id in content_types_with_shares:
            content_type = ContentType.objects.get(id=content_type_id)
            model = content_type.model_class()

            if not hasattr(model(), 'share_count'):
                logger.info('Model "{0}" does not have a "share_count" '
                            'attribute  Skipping this content type.'.format(
                                                                        model))
                continue

            # get the object ids for the content type that have shares
            model_ids_with_shares = Activity.objects.filter(
                about_content_type=content_type,
                action=Action.SHARED
            ).order_by('about_id').distinct('about_id').values_list('about_id',
                                                                    flat=True)

            total_objects_updated += len(model_ids_with_shares)

            for obj in model.objects.filter(id__in=model_ids_with_shares):
                obj.share_count = Activity.objects.filter(
                    about_content_type=content_type,
                    about_id=obj.id,
                    action=Action.SHARED
                ).count()

                logger.info('Updating {0} "{1}" with share_count of {2}'.format(
                    obj.get_verbose_name(),
                    obj,
                    obj.share_count
                ))

                if not dry_run:
                    obj.save()

        end = datetime.utcnow()
        total_seconds = (end - start).seconds
        logger.info('Updated {0} object share_count fields in {1} seconds!'.format(
            total_objects_updated,
            total_seconds
        ))
