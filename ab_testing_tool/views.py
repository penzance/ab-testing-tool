from django.http.response import HttpResponse
from django.core.urlresolvers import reverse
from django.shortcuts import render, render_to_response, redirect

from django_auth_lti.decorators import lti_role_required
from django_auth_lti.const import (ADMINISTRATOR, CONTENT_DEVELOPER,
    TEACHING_ASSISTANT, INSTRUCTOR)
from ims_lti_py.tool_config import ToolConfig
from django.views.decorators.http import require_http_methods
from django.utils.http import urlencode
from django.template.base import Template
from random import randint
from django.template.context import Context
from django.template import loader

ADMINS = [ADMINISTRATOR, CONTENT_DEVELOPER, TEACHING_ASSISTANT, INSTRUCTOR]

@lti_role_required(ADMINS)
def index(request):
    #print request
    #print request.__dict__
    return HttpResponse("index")
    #return render_to_response("admin.html")

def not_authorized(request):
    return HttpResponse("Student")

def lti_launch(request):
    return resource_selection(request)

def resource_selection(request):
    """ docs: https://canvas.instructure.com/doc/api/file.link_selection_tools.html """
    ext_content_return_types = request.REQUEST.get('ext_content_return_types')
    if ext_content_return_types == [u'lti_launch_url']:
        return HttpResponse("Error: invalid ext_content_return_types: %s" %
                            ext_content_return_types)
    content_return_url = request.REQUEST.get('ext_content_return_url')
    if not content_return_url:
        return HttpResponse("Error: no ext_content_return_url")
    
    return HttpResponse(loader.get_template("add_module_item.html").render(Context({"content_return_url": content_return_url})))

def submit_selection(request):
    page_url = "/%s" % randint(1000000000, 9999999999) #TODO: improve uniqueness
    page_name = request.REQUEST.get("page_name")#"A/B Page"
    content_return_url = request.REQUEST.get("content_return_url")
    
    if request.is_secure():
        host = "https://" + request.get_host()
    else:
        host = "http://" + request.get_host()
    lti_launch_url = "%s%s" % (host, page_url)
    params = {"return_type": "lti_launch_url",
               "url": lti_launch_url,
               #"title": "Title",
               "text": page_name}
    return redirect("%s?%s" % (content_return_url, urlencode(params)))

@require_http_methods(["GET"])
def tool_config(request):
    if request.is_secure():
        host = "https://" + request.get_host()
    else:
        host = "http://" + request.get_host()
    
    url = host + reverse("lti_launch")
    
    config = ToolConfig(
        title="A/B Testing Tool",
        launch_url=url,
        secure_launch_url=url,
    )
    # Tell Canvas that this tool provides a course navigation link:
    nav_params = {
        "enabled": "true",
        # optionally, supply a different URL for the link:
        # "url": "http://library.harvard.edu",
        "text": "A/B Testing Tool",
        "visibility": "admins",
    }
    config.set_ext_param("canvas.instructure.com", "privacy_level", "public")
    config.set_ext_param("canvas.instructure.com", "course_navigation",
                         nav_params)
    config.set_ext_param("canvas.instructure.com", "resource_selection",
                         {"enabled": "true", "url": host + reverse("index")})
    config.set_ext_param("canvas.instructure.com", "selection_height", "400")
    config.set_ext_param("canvas.instructure.com", "selection_width", "600")
    config.set_ext_param("canvas.instructure.com", "tool_id", "ab_testing_tool")
    config.description = ("Tool to allow students in a course to " +
                          "get different content in a module item.")
    
    resp = HttpResponse(config.to_xml(), content_type="text/xml", status=200)
    return resp
