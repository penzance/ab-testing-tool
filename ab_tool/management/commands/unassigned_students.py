from django.core.management.base import BaseCommand, CommandError

from ab_tool.canvas import get_unassigned_students_with_stored_credentials
from ab_tool.exceptions import NoValidCredentials
from ab_tool.models import CourseNotification, Experiment

class Command(BaseCommand):
    args = ""
    help = "Sends email alerts about courses with unassigned students"
    
    def handle(self, *args, **options):
        # TODO: update notification messages
        # TODO: Include intent-to-treat experiments when that is supported
        for experiment in Experiment.get_all_started_csv():
            course_notification = experiment.get_course_notification()
            # Check whether or not a notification can be sent to avoid extra API calls
            if not course_notification.can_notify():
                continue
            try:
                students = get_unassigned_students_with_stored_credentials(course_notification, experiment)
                if students:
                    self.send_email_notification(course_notification, "unnasigned students")
            except NoValidCredentials:
                self.send_email_notification(course_notification, "no valid credentials")
    
    def send_email_notification(self, course, message):
        # Potentially redundant notification check in case this method is used
        # in other places in the future
        if course.can_notify():
            self.stdout.write(str(course.get_emails()))
            self.stdout.write("TODO: send email %s" % message)
            course.notification_sent()
