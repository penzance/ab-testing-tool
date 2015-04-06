from django.core.urlresolvers import reverse
from django.http.response import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django_auth_lti.decorators import lti_role_required
from django.template.defaultfilters import slugify
from django.template import loader
from ims_lti_py.tool_config import ToolConfig
from intervention_point_pages import get_ip_open_where_display_index
from ab_tool.canvas import (get_lti_param, CanvasModules,
    experiments_with_unassigned_students)
from ab_tool.controllers import post_param
from ab_tool.models import (InterventionPoint, Experiment)
from ab_tool.constants import ADMINS
from ab_tool.spreadsheets import (get_student_list_csv,
    get_intervention_point_interactions_csv)


def not_authorized(request):
    return HttpResponse(loader.render_to_string("ab_tool/not_authorized.html"), status=401)


@csrf_exempt
@lti_role_required(ADMINS)
def render_control_panel(request):
    # retrieve the resource_link_id from lti_launch
    resource_link_id = get_lti_param(request, "resource_link_id")
    canvas_modules = CanvasModules(request)
    course_id = get_lti_param(request, "custom_canvas_course_id")
    intervention_points = InterventionPoint.objects.filter(course_id=course_id)
    ip_display_mappings = {track_url.id: get_ip_open_where_display_index(track_url)
                           for ip in intervention_points for track_url in ip.track_urls()}
    experiments = Experiment.objects.filter(course_id=course_id)
    
    context = {
        "resource_link_id": resource_link_id,
        "modules": canvas_modules.get_modules_with_items(resource_link_id),
        "intervention_points": intervention_points,
        "ip_display_mappings": ip_display_mappings,
        "uninstalled_intervention_points": canvas_modules.get_uninstalled_intervention_points(resource_link_id),
        "canvas_url": get_lti_param(request, "launch_presentation_return_url"),
        "experiments": experiments,
        "experiments_with_unassigned_students": experiments_with_unassigned_students(request, course_id),
        "deletable_experiment_ids": canvas_modules.get_deletable_experiment_ids(resource_link_id),
    }
    return render(request, "ab_tool/experiments_dashboard.html", context)


def tool_config(request):
    index_url = request.build_absolute_uri(reverse("ab_testing_tool_index"))
    resource_selection_url = request.build_absolute_uri(reverse("ab_testing_tool_resource_selection"))
    
    config = ToolConfig(
        title="A/B Testing Tool",
        launch_url=index_url,
        secure_launch_url=index_url,
    )
    # Tell Canvas that this tool provides a course navigation link:
    nav_params = {
        "enabled": "true",
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


@lti_role_required(ADMINS)
def download_track_assignments(request, experiment_id):
    #TODO: change this to streaming
    course_id = get_lti_param(request, "custom_canvas_course_id")
    course_title = get_lti_param(request, "context_title")
    experiment = Experiment.get_or_404_check_course(experiment_id, course_id)
    file_title = "course_%s_experiment_%s_student_track_assignments.csv" % (
                                slugify(course_title), slugify(experiment.name))
    return get_student_list_csv(experiment, file_title)


@lti_role_required(ADMINS)
def download_intervention_point_interactions(request, experiment_id):
    course_id = get_lti_param(request, "custom_canvas_course_id")
    course_title = get_lti_param(request, "context_title")
    experiment = Experiment.get_or_404_check_course(experiment_id, course_id)
    file_title = "course_%s_experiment_%s_intervention_point_interactions.csv" % (
                                slugify(course_title), slugify(experiment.name))
    return get_intervention_point_interactions_csv(experiment, file_title)
