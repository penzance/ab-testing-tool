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
from ab_testing_tool.models import Treatment, Track, StageUrl


ADMINS = [ADMINISTRATOR, CONTENT_DEVELOPER, TEACHING_ASSISTANT, INSTRUCTOR]
STAGE_URL_TAG = '_stageurl_'

def not_authorized(request):
    return HttpResponse("Student")


def get_module_items(all_modules, request_context, course_id):
    for module in all_modules:
        module["module_items"] = parse_response(list_module_items(request_context, course_id, module["id"], "content_details"))
    return all_modules

@lti_role_required(ADMINS)
def render_treatment_control_panel(request):
    course_id = get_lti_param(request, "custom_canvas_course_id")
    request_context = get_canvas_request_context(request)
    response = list_modules(request_context, course_id, "content_details")
    all_modules = parse_response(response)
    modules = get_module_items(all_modules, request_context, course_id)
    # TODO: instead of 'treatments = get_uninstalled_treatments(request)',render all treatments
    treatments = Treatment.objects.all()
    tracks = Track.objects.all()
    context = {"modules": modules,
               "treatments": treatments,
               "tracks": tracks,
               "canvas_url": get_lti_param(request, "launch_presentation_return_url")
              }
    return render_to_response("control_panel.html", context)


def deploy_treatment(request, t_id):
    """
    Delivers randomly one of the two urls in treatment.
    TODO: Extend this by delivering treatment as determined by track student is on
    TODO: Have admin able to preview treatments as a student would see them
    """
    # TODO: replace the following three lines with verification.is_allowed
    # when that code makes it into django_auth_lti master
    lti_launch = request.session.get('LTI_LAUNCH', None)
    user_roles = lti_launch.get('roles', [])
    if set(ADMINS) & set(user_roles):
        return redirect(reverse("edit_treatment", args=(t_id,)))
    t = Treatment.objects.get(pk=t_id)
    if bool(getrandbits(1)):
        return redirect(t.treatment_url1)
    else:
        return redirect(t.treatment_url2)

@lti_role_required(ADMINS)
def new_track(request):
    return render_to_response("edit_track.html")

@lti_role_required(ADMINS)
def edit_track(request, track_id):
    context = {"track": Track.objects.get(pk=track_id)}
    return render_to_response("edit_track.html", context)

@lti_role_required(ADMINS)
def create_track(request):
    course_id = get_lti_param(request, "custom_canvas_course_id")
    name = request.POST["name"]
    notes = request.POST["notes"]
    Track.objects.create(name=name, notes=notes, course_id=course_id)
    return redirect("/")

@lti_role_required(ADMINS)
def update_track(request):
    course_id = get_lti_param(request, "custom_canvas_course_id")
    name = request.POST["name"]
    notes = request.POST["notes"]
    track_id = request.POST["id"]
    result_list = Track.objects.filter(pk=track_id, course_id=course_id)
    if len(result_list) == 1:
        result_list[0].update(name=name, notes=notes)
    elif len(result_list) > 1:
        raise Exception("Multiple objects returned.")
    else:
        raise Exception("No track with ID '{0}' found".format(track_id))
    return redirect("/")

@lti_role_required(ADMINS)
def new_treatment(request):
    """
    Note: Canvas fetches all pages within iframe with POST request,
    requiring separate template render function.
    This also breaks CSRF token validation if CSRF Middleware is turned off.
    """
    context = {"tracks" : [(t,None) for t in Track.objects.all()]}
    return render_to_response("edit_treatment.html", context)


@lti_role_required(ADMINS)
def create_treatment(request):
    """
    Note: request will always be POST because Canvas fetches pages within iframe by POST
    TODO: use Django forms library to save instead of getting individual POST params
    """
    course_id = get_lti_param(request, "custom_canvas_course_id")
    name = request.POST["name"]
    notes = request.POST["notes"]
    t = Treatment.objects.create(name=name, notes=notes, course_id=course_id)
    stageurls = [(k,v) for (k,v) in request.POST.iteritems() if STAGE_URL_TAG in k and v]
    for (k,v) in stageurls:
        _,track_id = k.split(STAGE_URL_TAG)
        StageUrl.objects.create(url=v, stage_id=t.id, track_id=track_id)
    return redirect("/#tabs-2")


@lti_role_required(ADMINS)
def update_treatment(request):
    """
    Update treatment only allowed if admin has privileges on the particular course.
    TODO: use Django forms library to save instead of getting individual POST params
    """
    course_id = get_lti_param(request, "custom_canvas_course_id")
    name = request.POST["name"]
    notes = request.POST["notes"]
    t_id = request.POST["id"]
    result_list = Treatment.objects.filter(pk=t_id, course_id=course_id)
    if len(result_list) == 1:
        result_list[0].update(name=name, notes=notes)
    elif len(result_list) > 1:
        raise Exception("Multiple objects returned.")
    else:
        raise Exception("No stage with ID '{0}' found".format(t_id))
    #StageUrl creation
    stageurls = [(k,v) for (k,v) in request.POST.iteritems() if STAGE_URL_TAG in k and v]
    for (k,v) in stageurls:
        _,track_id = k.split(STAGE_URL_TAG)
        stage_result_list = StageUrl.objects.filter(stage__pk=t_id, track__pk=track_id)
        if len(stage_result_list) == 1:
            stage_result_list[0].update(url=v)
        elif len(result_list) > 1:
            raise Exception("Multiple objects returned.")
        else:
            StageUrl.objects.create(url=v, stage_id=t_id, track_id=track_id)
    return redirect("/#tabs-2")


@lti_role_required(ADMINS)
def edit_treatment(request, t_id):
    all_tracks = Track.objects.all()
    track_urls = []
    for t in all_tracks:
        stage_url = StageUrl.objects.filter(stage__pk=t_id, track=t)
        if stage_url:
            track_urls.append((t, stage_url[0]))
        else:
            track_urls.append((t, None))
    context = {"treatment": Treatment.objects.get(pk=t_id),
               "tracks": track_urls,
               }
    return render_to_response("edit_treatment.html", context)

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
    config.set_ext_param("canvas.instructure.com", "selection_height", "800")
    config.set_ext_param("canvas.instructure.com", "selection_width", "800")
    config.set_ext_param("canvas.instructure.com", "tool_id", "ab_testing_tool")
    config.description = ("Tool to allow students in a course to " +
                          "get different content in a module item.")

    resp = HttpResponse(config.to_xml(), content_type="text/xml", status=200)
    return resp
