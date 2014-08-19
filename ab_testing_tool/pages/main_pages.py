from django.core.urlresolvers import reverse
from django.http.response import HttpResponse
from django.shortcuts import render_to_response
#from django.views.decorators.csrf import csrf_exempt
#from django.views.decorators.clickjacking import xframe_options_exempt
from django_auth_lti.decorators import lti_role_required
from django_auth_lti.const import (ADMINISTRATOR, CONTENT_DEVELOPER,
    TEACHING_ASSISTANT, INSTRUCTOR)
from ims_lti_py.tool_config import ToolConfig

from ab_testing_tool.canvas import list_modules, get_module_items, get_lti_param
from ab_testing_tool.controllers import get_canvas_request_context
from ab_testing_tool.models import Stage, Track
from ab_testing_tool.decorators import page


ADMINS = [ADMINISTRATOR, CONTENT_DEVELOPER, TEACHING_ASSISTANT, INSTRUCTOR]
STAGE_URL_TAG = 'stageurl_'

@page
def not_authorized(request):
    return HttpResponse("Student")


@lti_role_required(ADMINS)
@page
def render_stage_control_panel(request):
    course_id = get_lti_param(request, "custom_canvas_course_id")
    request_context = get_canvas_request_context(request)
    all_modules = list_modules(request_context, course_id)
    modules = get_module_items(all_modules, request_context, course_id)
    # TODO: instead of 'stages = get_uninstalled_stages(request)',render all stages
    stages = Stage.objects.all()
    tracks = Track.objects.all()
    context = {"modules": modules,
               "stages": stages,
               "tracks": tracks,
               "canvas_url": get_lti_param(request, "launch_presentation_return_url")
              }
    return render_to_response("control_panel.html", context)


@page
def tool_config(request):
    index_url = request.build_absolute_uri(reverse("index"))
    resource_selection_url = request.build_absolute_uri(reverse("resource_selection"))
    
    config = ToolConfig(
        title="A/B Testing Tool",
        launch_url=index_url,
        secure_launch_url=index_url,
    )
    # Tell Canvas that this tool provides a course navigation link:
    nav_params = {
        "enabled": "true",
        # optionally, supply a different URL for the link:
        "url": index_url,
        "text": "A/B Testing Tool",
        "visibility": "admins",
    }
    config.set_ext_param("canvas.instructure.com", "privacy_level", "public")
    config.set_ext_param("canvas.instructure.com", "course_navigation",
                         nav_params)
    config.set_ext_param("canvas.instructure.com", "resource_selection",
                         {"enabled": "true", "url": resource_selection_url})
    config.set_ext_param("canvas.instructure.com", "selection_height", "800")
    config.set_ext_param("canvas.instructure.com", "selection_width", "800")
    config.set_ext_param("canvas.instructure.com", "tool_id", "ab_testing_tool")
    config.description = ("Tool to allow students in a course to " +
                          "get different content in a module item.")
    
    resp = HttpResponse(config.to_xml(), content_type="text/xml", status=200)
    return resp
