from datetime import datetime
from logging import getLogger
from activities.cleanup import ActivityCleaner
from django.core.management.base import BaseCommand


logging = getLogger(__name__)

class Command(BaseCommand):
    """Base class for updating remote object data."""

    def add_arguments(self, parser):
        parser.add_argument('-d', '--dry_run',
                            dest='dry_run',
                            default=False,
                            type=bool,
                            help=('boolean indicating if the images should '
                                  'actually be processed or if the function '
                                  'out just wants to be seen.'))

    def handle(self, ids=None, dry_run=False, *args, **options):
        """
        :param dry_run: boolean indicating if the objects should actually be
            processed or if the function out just wants to be seen.
        """
        if dry_run == True:
            logging.info('"dry_run" has been set to true. No actual '
                         'objects will be deleted while issuing this '
                         'command.')

        start = datetime.utcnow()
        cleaner = ActivityCleaner()
        cleaner.cleanup(is_dry_run=dry_run)
        end = datetime.utcnow()
        total_seconds = (end - start).seconds
        logging.info('Cleaned up activities in {0} seconds!'.format(
            total_seconds)
        )
