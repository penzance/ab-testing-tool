from django.http.response import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.clickjacking import xframe_options_exempt
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import render, render_to_response, redirect

from django_auth_lti.decorators import lti_role_required
from django_auth_lti import const

ADMINS = [const.INSTRUCTOR,const.TEACHING_ASSISTANT,const.ADMINISTRATOR,const.CONTENT_DEVELOPER]

@xframe_options_exempt
@csrf_exempt
#@lti_role_required(ADMINS, redirect_url=reverse_lazy("student_home"), raise_exception=True)
def index(request):
    return render_to_response("admin.html")
    #return HttpResponse("Welcome administrator.")

@xframe_options_exempt
@csrf_exempt
def student_home(request):
    return HttpResponse("Welcome student.")

