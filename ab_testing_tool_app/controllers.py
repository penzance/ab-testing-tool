from django.core.urlresolvers import reverse

from ab_testing_tool_app.models import Stage
from ab_testing_tool_app.canvas import (get_canvas_request_context, list_module_items, list_modules,
    get_lti_param)
from ab_testing_tool_app.exceptions import BAD_STAGE_ID, missing_param_error
from error_middleware.middleware import RenderableError


def stage_url(request, stage_id):
    """ Builds a URL to deploy the stage with the database id stage_id """
    try:
        stage_id = int(stage_id)
    except (TypeError, ValueError):
        raise BAD_STAGE_ID
    return request.build_absolute_uri(reverse("deploy_stage", args=(stage_id,)))


def format_url(url):
    """ Adds "http://" to the beginning of a url if it isn't there """
    if url.startswith("http://") or url.startswith("https://"):
        return url
    return "http://%s" % url


def get_uninstalled_stages(request):
    """ Returns the list of Stage objects that have been created for the
        current course but not installed in any of that course's modules """
    course_id = get_lti_param(request, "custom_canvas_course_id")
    installed_stage_urls = get_installed_stages(request)
    stages = [stage for stage in Stage.objects.filter(course_id=course_id)
              if stage_url(request, stage.id) not in installed_stage_urls]
    return stages


def get_installed_stages(request):
    """ Returns the list of stage urls (as strings) for Stages that have been
        installed in at least one of the courses modules. """
    course_id = get_lti_param(request, "custom_canvas_course_id")
    request_context =  get_canvas_request_context(request)
    all_modules = list_modules(request_context, course_id)
    installed_stage_urls = []
    for module in all_modules:
        module_items = list_module_items(request_context, course_id, module["id"])
        stage_urls = [item["external_url"] for item in module_items
                      if item["type"] == "ExternalTool"]
        installed_stage_urls.extend(stage_urls)
    return installed_stage_urls

def stage_is_installed(request, stage):
    return stage_url(request, stage.id) in get_installed_stages(request)

def get_incomplete_stages(stage_list):
    """ Takes paramter stage_list instead of parameter course_id to avoid
        second database call to the Stage table in methods that needs to
        already fetch the Stage table"""
    return [stage.name for stage in stage_list if stage.is_missing_urls()]

def all_stage_urls(request, course_id):
    """ Returns the deploy urls of all stages in the database for that course"""
    return [stage_url(request, stage.id) for stage in
            Stage.objects.filter(course_id=course_id)]


def get_modules_with_items(request):
    """
    Returns a list of all modules with the items of that module added to the
    module under the extra attribute "module_items" (this is a list).
    Each item in those lists has the added attribute "is_stage", which is a
    boolean describing whether or not the item is a stage of the ab_testing_tool
    """
    course_id = get_lti_param(request, "custom_canvas_course_id")
    request_context = get_canvas_request_context(request)
    stage_urls = all_stage_urls(request, course_id)
    modules = list_modules(request_context, course_id)
    for module in modules:
        module["module_items"] = list_module_items(request_context, course_id,
                                                   module["id"])
        for item in module["module_items"]:
            is_stage = (item["type"] == "ExternalTool" and "external_url" in item
                        and item["external_url"] in stage_urls)
            item["is_stage"] = is_stage
    return modules


def post_param(request, param_name):
    if param_name in request.POST:
        return request.POST[param_name]
    raise missing_param_error(param_name)
