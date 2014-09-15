from django_auth_lti.const import (ADMINISTRATOR, CONTENT_DEVELOPER,
    TEACHING_ASSISTANT, INSTRUCTOR)


ADMINS = [ADMINISTRATOR, CONTENT_DEVELOPER, TEACHING_ASSISTANT, INSTRUCTOR]
STAGE_URL_TAG = 'stageurl_'

UNKNOWN_ERROR_STRING = "An unknown error occurred in the A/B testing tool"
DOUBLE_ERROR_STRING = "A severe error occurred in the A/B testing tool"
