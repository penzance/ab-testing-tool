from django.core.urlresolvers import reverse

from ab_tool.models import InterventionPoint
from ab_tool.canvas import (get_canvas_request_context, list_module_items, list_modules,
    get_lti_param)
from ab_tool.exceptions import BAD_STAGE_ID, missing_param_error
from error_middleware.middleware import RenderableError


def intervention_point_url(request, intervention_point_id):
    """ Builds a URL to deploy the intervention_point with the database id intervention_point_id """
    try:
        intervention_point_id = int(intervention_point_id)
    except (TypeError, ValueError):
        raise BAD_STAGE_ID
    return request.build_absolute_uri(reverse("ab:deploy_intervention_point", args=(intervention_point_id,)))


def format_url(url):
    """ Adds "http://" to the beginning of a url if it isn't there """
    if url.startswith("http://") or url.startswith("https://"):
        return url
    return "http://%s" % url


def get_uninstalled_intervention_points(request):
    """ Returns the list of InterventionPoint objects that have been created for the
        current course but not installed in any of that course's modules """
    course_id = get_lti_param(request, "custom_canvas_course_id")
    installed_intervention_point_urls = get_installed_intervention_points(request)
    intervention_points = [intervention_point for intervention_point in InterventionPoint.objects.filter(course_id=course_id)
              if intervention_point_url(request, intervention_point.id) not in installed_intervention_point_urls]
    return intervention_points


def get_installed_intervention_points(request):
    """ Returns the list of InterventionPointUrls (as strings) for InterventionPoints that have been
        installed in at least one of the courses modules. """
    course_id = get_lti_param(request, "custom_canvas_course_id")
    request_context =  get_canvas_request_context(request)
    all_modules = list_modules(request_context, course_id)
    installed_intervention_point_urls = []
    for module in all_modules:
        module_items = list_module_items(request_context, course_id, module["id"])
        intervention_point_urls = [item["external_url"] for item in module_items
                      if item["type"] == "ExternalTool"]
        installed_intervention_point_urls.extend(intervention_point_urls)
    return installed_intervention_point_urls

def intervention_point_is_installed(request, intervention_point):
    return intervention_point_url(request, intervention_point.id) in get_installed_intervention_points(request)

def get_incomplete_intervention_points(intervention_point_list):
    """ Takes paramter intervention_point_list instead of parameter course_id to avoid
        second database call to the InterventionPoint table in methods that needs to
        already fetch the InterventionPoint table"""
    return [intervention_point.name for intervention_point in intervention_point_list if intervention_point.is_missing_urls()]

def all_intervention_point_urls(request, course_id):
    """ Returns the deploy urls of all intervention_points in the database for that course"""
    return [intervention_point_url(request, intervention_point.id) for intervention_point in
            InterventionPoint.objects.filter(course_id=course_id)]


def get_modules_with_items(request):
    """
    Returns a list of all modules with the items of that module added to the
    module under the extra attribute "module_items" (this is a list).
    Each item in those lists has the added attribute "is_intervention_point", which is a
    boolean describing whether or not the item is a intervention_point of the ab_testing_tool
    """
    course_id = get_lti_param(request, "custom_canvas_course_id")
    request_context = get_canvas_request_context(request)
    intervention_point_urls = all_intervention_point_urls(request, course_id)
    modules = list_modules(request_context, course_id)
    for module in modules:
        module["module_items"] = list_module_items(request_context, course_id,
                                                   module["id"])
        for item in module["module_items"]:
            is_intervention_point = (item["type"] == "ExternalTool" and "external_url" in item
                        and item["external_url"] in intervention_point_urls)
            item["is_intervention_point"] = is_intervention_point
    return modules


def post_param(request, param_name):
    if param_name in request.POST:
        return request.POST[param_name]
    raise missing_param_error(param_name)
