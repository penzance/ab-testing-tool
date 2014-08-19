from ab_testing_tool.models import Stage
from canvas import (get_canvas_request_context, list_module_items, list_modules,
    get_lti_param)
from django.core.urlresolvers import reverse


def stage_url(request, stage_id):
    """ Builds a URL to deploy the stage with the database id stage_id """
    return request.build_absolute_uri(reverse("deploy_stage", args=(stage_id,)))


def get_uninstalled_stages(request):
    """ Returns the list of Stage objects that have been created for the
        current course but not installed in any of that course's modules """
    course_id = get_lti_param(request, "custom_canvas_course_id")
    request_context =  get_canvas_request_context(request)
    all_modules = list_modules(request_context, course_id)
    installed_stage_urls = []
    for module in all_modules:
        module_items = list_module_items(request_context, course_id, module["id"])
        stage_urls = [item["external_url"] for item in module_items
                      if item["type"] == "ExternalTool"]
        installed_stage_urls.extend(stage_urls)
    stages = [stage for stage in Stage.objects.filter(course_id=course_id)
              if stage_url(request, stage.id) not in installed_stage_urls]
    return stages


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
