from django.shortcuts import render_to_response, redirect, get_object_or_404
from django_auth_lti.decorators import lti_role_required

from ab_testing_tool_app.constants import ADMINS
from ab_testing_tool_app.models import Track, CourseSettings, InterventionPoint
from ab_testing_tool_app.canvas import get_lti_param
from ab_testing_tool_app.exceptions import (UNAUTHORIZED_ACCESS,
    COURSE_TRACKS_ALREADY_FINALIZED, NO_TRACKS_FOR_COURSE)
from django.http.response import HttpResponse
from ab_testing_tool_app.controllers import (post_param, get_incomplete_stages)


@lti_role_required(ADMINS)
def create_track(request):
    course_id = get_lti_param(request, "custom_canvas_course_id")
    if CourseSettings.get_is_finalized(course_id):
        raise COURSE_TRACKS_ALREADY_FINALIZED
    return render_to_response("edit_track.html")


@lti_role_required(ADMINS)
def edit_track(request, track_id):
    track = get_object_or_404(Track, pk=track_id)
    course_id = get_lti_param(request, "custom_canvas_course_id")
    if course_id != track.course_id:
        raise UNAUTHORIZED_ACCESS
    is_finalized = CourseSettings.get_is_finalized(course_id)
    context = {"track": track,
               "is_finalized": is_finalized}
    return render_to_response("edit_track.html", context)


@lti_role_required(ADMINS)
def submit_create_track(request):
    course_id = get_lti_param(request, "custom_canvas_course_id")
    if CourseSettings.get_is_finalized(course_id):
        raise COURSE_TRACKS_ALREADY_FINALIZED
    name = post_param(request, "name")
    notes = post_param(request, "notes")
    Track.objects.create(name=name, notes=notes, course_id=course_id)
    return redirect("/")


@lti_role_required(ADMINS)
def submit_edit_track(request, track_id):
    track = get_object_or_404(Track, pk=track_id)
    course_id = get_lti_param(request, "custom_canvas_course_id")
    name = post_param(request, "name")
    notes = post_param(request, "notes")
    if course_id != track.course_id:
        raise UNAUTHORIZED_ACCESS
    track.update(name=name, notes=notes)
    return redirect("/")


@lti_role_required(ADMINS)
def delete_track(request, track_id):
    """
    NOTE: When a track gets deleted, urls for that track get deleted from all
          stages in that course as a result of cascading delete.
    """
    track = get_object_or_404(Track, pk=track_id)
    course_id = get_lti_param(request, "custom_canvas_course_id")
    if CourseSettings.get_is_finalized(course_id):
        raise COURSE_TRACKS_ALREADY_FINALIZED
    if course_id != track.course_id:
        raise UNAUTHORIZED_ACCESS
    track.delete()
    return redirect("/")


@lti_role_required(ADMINS)
def finalize_tracks(request):
    course_id = get_lti_param(request, "custom_canvas_course_id")
    if Track.objects.filter(course_id=course_id).count() == 0:
        raise NO_TRACKS_FOR_COURSE
    stages = InterventionPoint.objects.filter(course_id=course_id)
    incomplete_stages = get_incomplete_stages(stages)
    if incomplete_stages:
        #TODO: replace with better error display
        return HttpResponse("URLs missing for these tracks in these Intervention Points: %s" % incomplete_stages)
    CourseSettings.set_finalized(course_id)
    return redirect("/")
