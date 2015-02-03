import logging
import traceback
from django.core.management.base import BaseCommand

from ab_tool.canvas import get_unassigned_students_with_stored_credentials
from ab_tool.exceptions import NoValidCredentials
from ab_tool.models import Course
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
        for course in Course.get_notification_courses():
            for experiment in course.experiments_to_check():
                try:
                    students = get_unassigned_students_with_stored_credentials(course, experiment)
                    if students:
                        send_email_notification(course, ASSIGN_STUDENTS_MESSAGE)
                except NoValidCredentials:
                    send_email_notification(course, NO_CREDENTIALS_MESSAGE)
