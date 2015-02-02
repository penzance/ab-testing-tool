from django.core.management.base import BaseCommand
from django.core.mail import send_mail

from ab_tool.canvas import get_unassigned_students_with_stored_credentials
from ab_tool.exceptions import NoValidCredentials
from ab_tool.models import Course
from ab_tool.constants import (ASSIGN_STUDENTS_MESSAGE, NO_CREDENTIALS_MESSAGE,
    FROM_EMAIL_ADDRESS)

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
                        self.send_email_notification(course, ASSIGN_STUDENTS_MESSAGE)
                except NoValidCredentials:
                    self.send_email_notification(course, NO_CREDENTIALS_MESSAGE)
    
    def send_email_notification(self, course, email):
        if course.can_notify():
            subject, message = email
            message += "\n\nCourse Id: %s\nCanvas URL: %s" % (course.course_id, course.canvas_url)
            send_mail(subject, message, FROM_EMAIL_ADDRESS,
                      course.get_emails(), fail_silently=False)
            course.notification_sent()
