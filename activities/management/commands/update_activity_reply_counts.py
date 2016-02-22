from datetime import datetime
from logging import getLogger

from activities.models import Activity
from activities.models import ActivityReply
from django.core.management.base import BaseCommand
from django.db.models.aggregates import Count


logging = getLogger(__name__)

class Command(BaseCommand):
    help = "Updates activity reply counts for all activities."

    def add_arguments(self, parser):
        parser.add_argument('--activity_ids',
                            nargs='+',
                            dest='activity_ids',
                            default=None,
                            type=int,
                            help=('An acitiity id or an space separated list '
                                  'of activity ids to update the reply counts '
                                  'for. If None, this will update all activity '
                                  'reply counts.'))
        parser.add_argument('-d', '--dry_run',
                            dest='dry_run',
                            default=False,
                            type=bool,
                            help=('boolean indicating if the images should '
                                  'actually be processed or if the function '
                                  'out just wants to be seen.'))

    def handle(self, activity_ids=None, dry_run=False, *args, **options):
        """
        :param activity_ids: list of activity id to update the reply counts for.
            If None, this will process all activities.
        :param dry_run: boolean indicating if the objects should actually be
            processed or if the function out just wants to be seen.
        """
        if dry_run == True:
            logging.info('"dry_run" has been set to true. No actual '
                         'updates will be made.')

        start = datetime.utcnow()

        # get all activity ids that have replies
        activity_ids = (ActivityReply.objects.all()
                                             .order_by('activity')
                                             .distinct('activity')
                                             .values_list('activity',
                                                          flat=True))

        logging.info('Updating all activities with no replies to have a '
                     'reply_count of 0...')

        if not dry_run:
            # Update all reply counts for other activities to 0
            Activity.objects.exclude(id__in=activity_ids).update(reply_count=0)

        queryset = Activity.objects.filter(
            id__in=activity_ids
        ).annotate(reply_count_actual=Count('replies'))

        logging.info('Starting to update activities...')

        # update all activities will replies to the correct count
        for activity in queryset:
            activity.reply_count = activity.reply_count_actual
            msg = 'Updating activity id: "{0}" with reply count of "{1}"'.format(
                activity.id,
                activity.reply_count_actual
            )
            logging.info(msg)

            if not dry_run:
                activity.save()

        end = datetime.utcnow()
        total_seconds = (end - start).seconds
        logging.info('Updated {0} activities reply counts in {1} seconds!'.format(
            len(activity_ids),
            total_seconds
        ))
