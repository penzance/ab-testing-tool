from django_auth_lti.const import (ADMINISTRATOR, CONTENT_DEVELOPER,
    TEACHING_ASSISTANT, INSTRUCTOR)


ADMINS = [ADMINISTRATOR, CONTENT_DEVELOPER, TEACHING_ASSISTANT, INSTRUCTOR]
STAGE_URL_TAG = 'intervention_point_url_'
DEPLOY_OPTION_TAG = 'is_canvas_page_for_track_'
AS_TAB_TAG = 'open_as_tab_for_track_'


ASSIGN_STUDENTS_MESSAGE = ("Missing Student Track Assignments",
""" New learners have joined your course.
This course has at least one experiment in the A/B Testing Tool that needs you
to assign tracks to these students. Please log in to canvas to fix this.
Until you do, these students will be unable to access some of the canvas content
for this course. """)

NO_CREDENTIALS_MESSAGE = ("Missing Canvas Credentials",
""" The A/B Testing Tool does not have permission to access
data from Canvas on your behalf. Please go to the A/B Testing Tool dashboard
for your course and log in to the tool to grant it access to your account. """)