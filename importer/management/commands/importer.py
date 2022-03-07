# https://docs.djangoproject.com/en/3.1/howto/custom-management-commands/
# https://feedparser.readthedocs.io/en/latest/

from django.core.management.base import BaseCommand

from ._reddit import do_import as do_reddit_import
from ._rss import do_import as do_rss_import
from ._mail import do_import as do_mail_import
from ._cleanup import do_cleanup
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):

    def handle(self, *args, **options):
        try:
            do_reddit_import()
        except Exception as e:
            logger.error(f'Error when trying to do reddit import : {e}')

        try:
            do_rss_import()
        except Exception as e:
            logger.error(f'Error when trying to do rss import : {e}')

        # try:
        #    do_mail_import()
        # except Exception as e:
        #    logger.error(f'Error when trying to do mail import : {e}')

        try:
            do_cleanup()
        except Exception as e:
            logger.error(f"Error when doing clean up : {e}")
