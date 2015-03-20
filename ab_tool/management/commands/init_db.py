import logging
import subprocess

from optparse import make_option

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Initialize abtest postgresql database'
    option_list = BaseCommand.option_list + (
        make_option(
            '--force',
            action='store_true',
            dest='force',
            default=False,
            help='Skip confirmation prompt'
        ),
    )

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

    def handle(self, *args, **options):
        try:
            if not options['force']:
                confirm = raw_input('This will drop your current abtest postgresql database. Are you sure? (n): ')
                if not confirm or confirm[:1].lower() != 'y':
                    return

            db_settings = settings.DATABASES.get('default')
            print db_settings
            db_name = db_settings.get('NAME')
            db_user = db_settings.get('USER')
            db_password = db_settings.get('PASSWORD')

            drop_user = "DROP USER IF EXISTS %s" % db_user
            create_user = "CREATE USER %s WITH PASSWORD '%s'" % (db_user, db_password)
            drop_db = "DROP DATABASE IF EXISTS %s" % db_name
            create_db = "CREATE DATABASE %s WITH OWNER %s" % (db_name, db_user)


            subprocess.call(['psql', '-d', 'postgres', '-c', drop_user])
            logger.info("Dropped user %s", db_user)
            subprocess.call(['psql', '-d', 'postgres', '-c', drop_db])
            logger.info("Dropped db %s", db_name)
            subprocess.call(['psql', '-d', 'postgres', '-c', create_user])
            logger.info("Created user %s", db_user)
            subprocess.call(['psql', '-d', 'postgres', '-c', create_db])
            logger.info("Created db %s with owner %s", db_name, db_user)
        except Exception:
            logger.exception('Error encountered while initializing abtest postgresql database:')
            raise CommandError('Failed to init abtest postgresql database')