import logging
import traceback
from django.core.management.base import BaseCommand

from ab_tool.canvas import get_unassigned_students_with_stored_credentials
from ab_tool.exceptions import NoValidCredentials
from ab_tool.models import Experiment
from ab_tool.constants import (ASSIGN_STUDENTS_MESSAGE, NO_CREDENTIALS_MESSAGE)
from ab_tool.controllers import send_email_notification


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    args = ""
    help = "Sends email alerts about courses with unassigned students"
    
    def handle(self, *args, **options):
        try:
            self.handle_core()
        except Exception as exception:
            logger.error(repr(exception))
            logger.error(traceback.format_exc())
            raise
    
    def handle_core(self):
        # TODO: Include intent-to-treat experiments when that is supported
        for experiment in Experiment.get_all_started_csv():
            course_notification = experiment.get_course_notification()
            # Check whether or not a notification can be sent to avoid extra API calls
            if not course_notification.can_notify():
                continue
            try:
                students = get_unassigned_students_with_stored_credentials(course_notification, experiment)
                if students:
                    send_email_notification(course, ASSIGN_STUDENTS_MESSAGE)
            except NoValidCredentials:
                send_email_notification(course, NO_CREDENTIALS_MESSAGE)
