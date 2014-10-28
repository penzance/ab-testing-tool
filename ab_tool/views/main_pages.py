import csv
from django.core.urlresolvers import reverse
from django.http.response import HttpResponse
from django.shortcuts import render_to_response, redirect, get_object_or_404
#from django.views.decorators.csrf import csrf_exempt
from django_auth_lti.decorators import lti_role_required
from django.template.defaultfilters import slugify
from django.template import loader
from ims_lti_py.tool_config import ToolConfig

from ab_tool.canvas import get_lti_param
from ab_tool.controllers import (get_uninstalled_intervention_points,
    get_modules_with_items, get_incomplete_intervention_points,
    get_missing_track_weights)
from ab_tool.models import (InterventionPoint, Track, CourseStudent,
    CourseSettings)
from ab_tool.constants import ADMINS
from ab_tool.exceptions import EXPERIMENT_TRACKS_ALREADY_FINALIZED


def not_authorized(request):
    return HttpResponse(loader.render_to_string("ab_tool/not_authorized.html"), status=401)


@lti_role_required(ADMINS)
def render_intervention_point_control_panel(request):
    course_id = get_lti_param(request, "custom_canvas_course_id")
    course_settings,_ = CourseSettings.objects.get_or_create(course_id=course_id)
    modules = get_modules_with_items(request)
    uninstalled_intervention_points = get_uninstalled_intervention_points(request)
    intervention_points = InterventionPoint.objects.filter(course_id=course_id)
    tracks = Track.objects.filter(course_id=course_id)
    is_finalized = CourseSettings.get_is_finalized(course_id=course_id)
    incomplete_intervention_points = get_incomplete_intervention_points(intervention_points)
    missing_track_weights = get_missing_track_weights(tracks, course_id)
    context = {
        "course_settings": course_settings,
        "modules": modules,
        "intervention_points": intervention_points,
        "uninstalled_intervention_points": uninstalled_intervention_points,
        "tracks": tracks,
        "canvas_url": get_lti_param(request, "launch_presentation_return_url"),
        "is_finalized": is_finalized,
        "incomplete_intervention_points": incomplete_intervention_points,
        "missing_track_weights": missing_track_weights,
    }
    return render_to_response("ab_tool/control_panel.html", context)


def tool_config(request):
    index_url = request.build_absolute_uri(reverse("ab:index"))
    resource_selection_url = request.build_absolute_uri(reverse("ab:resource_selection"))
    
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
def download_data(request):
    course_id = get_lti_param(request, "custom_canvas_course_id")
    course_title = get_lti_param(request, "context_title")
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = ('attachment; filename=%s_students.csv' %
                                       slugify(course_title))
    writer = csv.writer(response)
    # Write headers to CSV file
    headers = ["Student ID", "LIS Person Sourcedid", "Assigned Track",
               "Timestamp Last Updated"]
    writer.writerow(headers)
    # Write data to CSV file
    for s in CourseStudent.objects.filter(course_id=course_id):
        row = [s.student_id, s.lis_person_sourcedid, s.track.name, s.updated_on]
        writer.writerow(row)
    return response

@lti_role_required(ADMINS)
def submit_assignment_method(request):
    course_id = get_lti_param(request, "custom_canvas_course_id")
    if CourseSettings.get_is_finalized(course_id):
        raise EXPERIMENT_TRACKS_ALREADY_FINALIZED
    assignment_method = request.POST.get('assignment_method')
    course_settings = get_object_or_404(CourseSettings, course_id=course_id)
    course_settings.update(assignment_method=assignment_method)
    return redirect(reverse("ab:index") + "#tabs-5")
