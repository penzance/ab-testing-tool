from django.shortcuts import render_to_response, redirect
from django_auth_lti.decorators import lti_role_required

from ab_testing_tool_app.constants import ADMINS
from ab_testing_tool_app.models import Track, CourseSetting, Stage
from ab_testing_tool_app.canvas import get_lti_param
from ab_testing_tool_app.exceptions import (MISSING_TRACK, UNAUTHORIZED_ACCESS,
    COURSE_TRACKS_ALREADY_FINALIZED, NO_TRACKS_FOR_COURSE)
from django.http.response import HttpResponse
from ab_testing_tool_app.controllers import post_param


@lti_role_required(ADMINS)
def create_track(request):
    course_id = get_lti_param(request, "custom_canvas_course_id")
    if CourseSetting.get_is_finalized(course_id):
        raise COURSE_TRACKS_ALREADY_FINALIZED
    return render_to_response("edit_track.html")


@lti_role_required(ADMINS)
def edit_track(request, track_id):
    course_id = get_lti_param(request, "custom_canvas_course_id")
    t = Track.get_or_none(pk=track_id)
    if not t:
        raise MISSING_TRACK
    if course_id != t.course_id:
        raise UNAUTHORIZED_ACCESS
    is_finalized = CourseSetting.get_is_finalized(course_id)
    context = {"track": t,
               "is_finalized": is_finalized}
    return render_to_response("edit_track.html", context)


@lti_role_required(ADMINS)
def submit_create_track(request):
    course_id = get_lti_param(request, "custom_canvas_course_id")
    if CourseSetting.get_is_finalized(course_id):
        raise COURSE_TRACKS_ALREADY_FINALIZED
    name = post_param(request, "name")
    notes = post_param(request, "notes")
    Track.objects.create(name=name, notes=notes, course_id=course_id)
    return redirect("/")


@lti_role_required(ADMINS)
def submit_edit_track(request):
    course_id = get_lti_param(request, "custom_canvas_course_id")
    name = post_param(request, "name")
    notes = post_param(request, "notes")
    track_id = post_param(request, "id")
    track = Track.get_or_none(pk=track_id)
    if not track:
        raise MISSING_TRACK
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
    course_id = get_lti_param(request, "custom_canvas_course_id")
    if CourseSetting.get_is_finalized(course_id):
        raise COURSE_TRACKS_ALREADY_FINALIZED
    track = Track.get_or_none(pk=track_id)
    if not track:
        raise MISSING_TRACK
    if course_id != track.course_id:
        raise UNAUTHORIZED_ACCESS
    track.delete()
    return redirect("/")


@lti_role_required(ADMINS)
def finalize_tracks(request):
    course_id = get_lti_param(request, "custom_canvas_course_id")
    if Track.objects.filter(course_id=course_id).count() == 0:
        raise NO_TRACKS_FOR_COURSE
    missing_urls = [stage.name for stage
                    in Stage.objects.filter(course_id=course_id)
                    if stage.is_missing_urls()]
    if missing_urls:
        #TODO: replace with better error display
        return HttpResponse("URLs missing for these tracks in these Stages: %s" % missing_urls)
    CourseSetting.set_finalized(course_id)
    return redirect("/")
