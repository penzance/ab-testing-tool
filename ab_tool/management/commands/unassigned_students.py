from django.core.management.base import BaseCommand
from django.core.mail import send_mail

from ab_tool.canvas import get_unassigned_students_with_stored_credentials
from ab_tool.exceptions import NoValidCredentials
from ab_tool.models import Course

class Command(BaseCommand):
    args = ""
    help = "Sends email alerts about courses with unassigned students"
    
    def handle(self, *args, **options):
        # TODO: update notification messages
        for course in Course.get_notification_courses():
            for experiment in course.experiments_to_check():
                try:
                    students = get_unassigned_students_with_stored_credentials(course, experiment)
                    if students:
                        self.send_email_notification(course, "unnasigned students")
                except NoValidCredentials:
                    self.send_email_notification(course, "no valid credentials")
    
    def send_email_notification(self, course, message):
        if course.can_notify():
            self.stdout.write(str(course.get_emails()))
            self.stdout.write("TODO: send email %s" % message)
            course.notification_sent()
