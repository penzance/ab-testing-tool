from canvas_sdk.methods.modules import (list_module_items, list_modules,
    create_module_item)
from django.core.urlresolvers import reverse
from django.http.response import HttpResponse
from django.shortcuts import render_to_response, redirect
from django.utils.http import urlencode
from django.views.decorators.http import require_http_methods
#from django.views.decorators.csrf import csrf_exempt
#from django.views.decorators.clickjacking import xframe_options_exempt
from django_auth_lti.decorators import lti_role_required
from django_auth_lti.const import (ADMINISTRATOR, CONTENT_DEVELOPER,
    TEACHING_ASSISTANT, INSTRUCTOR)
from ims_lti_py.tool_config import ToolConfig
from random import getrandbits, randint

from ab_testing_tool.controllers import (get_lti_param, get_canvas_request_context,
    parse_response, get_uninstalled_treatments, treatment_url, get_full_host)
from ab_testing_tool.models import Treatment


ADMINS = [ADMINISTRATOR, CONTENT_DEVELOPER, TEACHING_ASSISTANT, INSTRUCTOR]


def not_authorized(request):
    return HttpResponse("Student")


@lti_role_required(ADMINS)
def render_treatment_control_panel(request):
    course_id = get_lti_param(request, "custom_canvas_course_id")
    request_context = get_canvas_request_context(request)
    response = list_modules(request_context, course_id, "content_details")
    all_modules = parse_response(response)
    treatments = get_uninstalled_treatments(request)
    
    context = {"modules": all_modules,
               "treatments": treatments,
               "canvas_url": get_lti_param(request, "launch_presentation_return_url")
              }
    return render_to_response("control_panel.html", context)


def deploy_treatment(request, t_id):
    """
    Delivers randomly one of the two urls in treatment.
    TODO: Extend this by delivering treatment as determined by track student is on
    """
    t = Treatment.objects.get(pk=t_id)
    if bool(getrandbits(1)):
        return redirect(t.treatment_url1)
    else:
        return redirect(t.treatment_url2)


@lti_role_required(ADMINS)
def new_treatment(request):
    """
    Note: Canvas fetches all pages within iframe with POST request,
    requiring separate template render function.
    This also breaks CSRF token validation if CSRF Middleware is turned off.
    """
    return render_to_response("edit_treatment.html")


@lti_role_required(ADMINS)
def create_treatment(request):
    """
    Note: request will always be POST because Canvas fetches pages within iframe by POST
    TODO: use Django forms library to save instead of getting individual POST params
    """
    course_id = get_lti_param(request, "custom_canvas_course_id")
    name = request.POST["name"]
    url1 = request.POST["url1"]
    url2 = request.POST["url2"]
    notes = request.POST["notes"]
    Treatment.objects.create(name=name, treatment_url1=url1, treatment_url2=url2, notes=notes, course_id=course_id)
    return redirect("/")


@lti_role_required(ADMINS)
def update_treatment(request):
    """
    Update treatment only allowed if admin has privileges on the particular course.
    TODO: use Django forms library to save instead of getting individual POST params
    """
    course_id = get_lti_param(request, "custom_canvas_course_id")
    name = request.POST["name"]
    url1 = request.POST["url1"]
    url2 = request.POST["url2"]
    notes = request.POST["notes"]
    t_id = request.POST["id"]
    result_list = Treatment.objects.filter(pk=t_id, course_id=course_id)
    if len(result_list) == 1:
        result_list[0].update(name=name, treatment_url1=url1, treatment_url2=url2, notes=notes)
    elif len(result_list) > 1:
        raise Exception("Multiple objects returned.")
    else:
        raise Exception("No treatment found")
    return redirect("/")


@lti_role_required(ADMINS)
def edit_treatment(request, t_id):
    return render_to_response("edit_treatment.html",
                              {"treatment": Treatment.objects.get(pk=t_id)})


@lti_role_required(ADMINS)
def add_treatment_to_module(request, t_id):
    """
    TODO: Finish this to be able to add treatment to a module from control panel
    """
    course_id = get_lti_param(request, "custom_canvas_course_id")
    request_context =  get_canvas_request_context(request)
    modules = list_modules(request_context, course_id, "content_details")
    item_results = list_module_items(request_context, course_id,
                                     "24", "content_details")
    module_id = modules[0]["id"]
    # canvas_sdk.methods.modules.create_module_item(
    #        request_ctx, course_id, module_id, module_item_type,
    #        module_item_content_id, module_item_page_url,
    #        module_item_external_url,
    #        module_item_completion_requirement_min_score)
    create_module_item(request_context, course_id, module_id, "ExternalTool",
                       "ab_testing_tool", "1", treatment_url(request, t_id),
                       None)
    return redirect("/")


def lti_launch(request):
    return treatment_selection(request)


def treatment_selection(request):
    """ docs: https://canvas.instructure.com/doc/api/file.link_selection_tools.html """
    ext_content_return_types = request.REQUEST.get('ext_content_return_types')
    if ext_content_return_types == [u'lti_launch_url']:
        return HttpResponse("Error: invalid ext_content_return_types: %s" %
                            ext_content_return_types)
    content_return_url = request.REQUEST.get('ext_content_return_url')
    if not content_return_url:
        return HttpResponse("Error: no ext_content_return_url")
    
    context = {"content_return_url": content_return_url,
               "treatments": get_uninstalled_treatments(request)}
    return render_to_response("add_module_item.html", context)


def submit_selection(request):
    treatment_id = request.REQUEST.get("treatment_id")
    page_url = treatment_url(request, treatment_id)
    print treatment_id, page_url
    page_name = "A/B Page" # TODO: replace with value from DB
    content_return_url = request.REQUEST.get("content_return_url")
    params = {"return_type": "lti_launch_url",
               "url": page_url,
               #"title": "Title",
               "text": page_name}
    return redirect("%s?%s" % (content_return_url, urlencode(params)))


def tool_config(request):
    host = get_full_host(request)
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
        "url": host + reverse("index"),
        "text": "A/B Testing Tool",
        "visibility": "admins",
    }
    config.set_ext_param("canvas.instructure.com", "privacy_level", "public")
    config.set_ext_param("canvas.instructure.com", "course_navigation",
                         nav_params)
    config.set_ext_param("canvas.instructure.com", "resource_selection",
                         {"enabled": "true", "url": host + reverse("lti_launch")})
    config.set_ext_param("canvas.instructure.com", "selection_height", "400")
    config.set_ext_param("canvas.instructure.com", "selection_width", "600")
    config.set_ext_param("canvas.instructure.com", "tool_id", "ab_testing_tool")
    config.description = ("Tool to allow students in a course to " +
                          "get different content in a module item.")
    
    resp = HttpResponse(config.to_xml(), content_type="text/xml", status=200)
    return resp
