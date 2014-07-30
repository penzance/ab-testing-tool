from django.http.response import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.clickjacking import xframe_options_exempt

from django_auth_lti.decorators import lti_role_required
from django_auth_lti.const import ADMINISTRATOR, CONTENT_DEVELOPER, TEACHING_ASSISTANT, INSTRUCTOR

ADMINS = [ADMINISTRATOR, CONTENT_DEVELOPER, TEACHING_ASSISTANT, INSTRUCTOR]

@lti_role_required(ADMINS)
def index(request):
    return HttpResponse("Hello world!")

def not_authorized(request):
    return HttpResponse("Student")
