from django_auth_lti.const import (ADMINISTRATOR, CONTENT_DEVELOPER,
    TEACHING_ASSISTANT, INSTRUCTOR)


ADMINS = [ADMINISTRATOR, CONTENT_DEVELOPER, TEACHING_ASSISTANT, INSTRUCTOR]
STAGE_URL_TAG = 'intervention_point_url_'
DEPLOY_OPTION_TAG = 'is_canvas_page_for_track_'
AS_TAB_TAG = 'open_as_tab_for_track_'


# TODO: change this to actual email address
FROM_EMAIL_ADDRESS = "no-reply@example.com"

ASSIGN_STUDENTS_MESSAGE = ("Missing Student Track Assignments",
""" New students have joined your canvas course.
This course has at least one experiment in the A/B Testing Tool that needs you
to assign tracks to these students.  Please log in to canvas to fix this.
Until you do, these students will be unable to access some of the canvas content
for this course. """)

NO_CREDENTIALS_MESSAGE = ("Missing Canvas Credentials",
""" The Canvas A/B Testing tool has no valid credentials
to access the canvas SDK on your behalf.  Please go to the A/B Testing Tool control
panel for your course and log in with canvas. """)
