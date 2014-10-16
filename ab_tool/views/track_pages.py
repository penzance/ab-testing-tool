from django.shortcuts import render_to_response, redirect, get_object_or_404
from django_auth_lti.decorators import lti_role_required
from django.core.urlresolvers import reverse

from ab_tool.constants import ADMINS
from ab_tool.models import (Track, CourseSettings, InterventionPoint)
from ab_tool.canvas import get_lti_param
from ab_tool.exceptions import (UNAUTHORIZED_ACCESS,
    COURSE_TRACKS_ALREADY_FINALIZED, NO_TRACKS_FOR_COURSE)
from django.http.response import HttpResponse
from ab_tool.controllers import (post_param, get_incomplete_intervention_points)


@lti_role_required(ADMINS)
def create_track(request):
    course_id = get_lti_param(request, "custom_canvas_course_id")
    if CourseSettings.get_is_finalized(course_id):
        raise COURSE_TRACKS_ALREADY_FINALIZED
    return render_to_response("ab_tool/edit_track.html")


@lti_role_required(ADMINS)
def edit_track(request, track_id):
    track = get_object_or_404(Track, pk=track_id)
    course_id = get_lti_param(request, "custom_canvas_course_id")
    if course_id != track.course_id:
        raise UNAUTHORIZED_ACCESS
    is_finalized = CourseSettings.get_is_finalized(course_id)
    context = {"track": track,
               "is_finalized": is_finalized}
    return render_to_response("ab_tool/edit_track.html", context)


@lti_role_required(ADMINS)
def submit_create_track(request):
    course_id = get_lti_param(request, "custom_canvas_course_id")
    if CourseSettings.get_is_finalized(course_id):
        raise COURSE_TRACKS_ALREADY_FINALIZED
    name = post_param(request, "name")
    notes = post_param(request, "notes")
    Track.objects.create(name=name, notes=notes, course_id=course_id)
    return redirect(reverse("ab:index"))


@lti_role_required(ADMINS)
def submit_edit_track(request, track_id):
    track = get_object_or_404(Track, pk=track_id)
    course_id = get_lti_param(request, "custom_canvas_course_id")
    name = post_param(request, "name")
    notes = post_param(request, "notes")
    if course_id != track.course_id:
        raise UNAUTHORIZED_ACCESS
    track.update(name=name, notes=notes)
    return redirect(reverse("ab:index"))


@lti_role_required(ADMINS)
def delete_track(request, track_id):
    """
    NOTE: When a track gets deleted, urls for that track get deleted from all
          intervention_points in that course as a result of cascading delete.
    """
    track = get_object_or_404(Track, pk=track_id)
    course_id = get_lti_param(request, "custom_canvas_course_id")
    if CourseSettings.get_is_finalized(course_id):
        raise COURSE_TRACKS_ALREADY_FINALIZED
    if course_id != track.course_id:
        raise UNAUTHORIZED_ACCESS
    track.delete()
    return redirect(reverse("ab:index"))


@lti_role_required(ADMINS)
def finalize_tracks(request):
    course_id = get_lti_param(request, "custom_canvas_course_id")
    if Track.objects.filter(course_id=course_id).count() == 0:
        raise NO_TRACKS_FOR_COURSE
    intervention_points = InterventionPoint.objects.filter(course_id=course_id)
    incomplete_intervention_points = get_incomplete_intervention_points(intervention_points)
    if incomplete_intervention_points:
        #TODO: replace with better error display
        return HttpResponse("URLs missing for these tracks in these Intervention Points: %s" % incomplete_intervention_points)
    CourseSettings.set_finalized(course_id)
    return redirect(reverse("ab:index"))

