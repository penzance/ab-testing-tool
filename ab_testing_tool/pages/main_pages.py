from ab_testing_tool.canvas import (list_module_items, list_modules, create_module_item, get_module_items)
from django.core.urlresolvers import reverse
from django.http.response import HttpResponse
from django.shortcuts import render_to_response, redirect
from django.views.decorators.http import require_http_methods
#from django.views.decorators.csrf import csrf_exempt
#from django.views.decorators.clickjacking import xframe_options_exempt
from django_auth_lti.decorators import lti_role_required
from django_auth_lti.const import (ADMINISTRATOR, CONTENT_DEVELOPER,
    TEACHING_ASSISTANT, INSTRUCTOR)
from ims_lti_py.tool_config import ToolConfig

from ab_testing_tool.controllers import (get_lti_param, get_canvas_request_context,
    parse_response, get_uninstalled_stages, stage_url, get_full_host)
from ab_testing_tool.models import Stage, Track, StageUrl


ADMINS = [ADMINISTRATOR, CONTENT_DEVELOPER, TEACHING_ASSISTANT, INSTRUCTOR]
STAGE_URL_TAG = '_stageurl_'

def not_authorized(request):
    return HttpResponse("Student")


@lti_role_required(ADMINS)
def render_stage_control_panel(request):
    course_id = get_lti_param(request, "custom_canvas_course_id")
    request_context = get_canvas_request_context(request)
    response = list_modules(request_context, course_id, "content_details")
    all_modules = parse_response(response)
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

def tool_config(request):
    host = get_full_host(request)
    url = host + reverse("index")

    config = ToolConfig(
        title="A/B Testing Tool",
        launch_url=url,
        secure_launch_url=url,
    )
    # Tell Canvas that this tool provides a course navigation link:
    nav_params = {
        "enabled": "true",
        # optionally, supply a different URL for the link:
        "url": host + reverse("index"),
        "text": "A/B Testing Tool",
        "visibility": "admins",
    }
    config.set_ext_param("canvas.instructure.com", "privacy_level", "public")
    config.set_ext_param("canvas.instructure.com", "course_navigation",
                         nav_params)
    config.set_ext_param("canvas.instructure.com", "resource_selection",
                         {"enabled": "true", "url": host + reverse("resource_selection")})
    config.set_ext_param("canvas.instructure.com", "selection_height", "800")
    config.set_ext_param("canvas.instructure.com", "selection_width", "800")
    config.set_ext_param("canvas.instructure.com", "tool_id", "ab_testing_tool")
    config.description = ("Tool to allow students in a course to " +
                          "get different content in a module item.")

    resp = HttpResponse(config.to_xml(), content_type="text/xml", status=200)
    return resp
