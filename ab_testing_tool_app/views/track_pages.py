from django.shortcuts import render_to_response, redirect
from django_auth_lti.decorators import lti_role_required

from ab_testing_tool_app.constants import ADMINS
from ab_testing_tool_app.models import Track, StageUrl
from ab_testing_tool_app.canvas import get_lti_param
from ab_testing_tool_app.decorators import page
from ab_testing_tool_app.exceptions import (MULTIPLE_OBJECTS, MISSING_TRACK,
    UNAUTHORIZED_ACCESS)
from ab_testing_tool_app.controllers import post_param


@lti_role_required(ADMINS)
@page
def create_track(request):
    return render_to_response("edit_track.html")


@lti_role_required(ADMINS)
@page
def edit_track(request, track_id):
    course_id = get_lti_param(request, "custom_canvas_course_id")
    t = Track.objects.get(pk=track_id)
    if course_id != t.course_id:
        raise UNAUTHORIZED_ACCESS
    context = {"track": t}
    return render_to_response("edit_track.html", context)


@lti_role_required(ADMINS)
@page
def submit_create_track(request):
    course_id = get_lti_param(request, "custom_canvas_course_id")
    name = post_param(request, "name")
    notes = post_param(request, "notes")
    Track.objects.create(name=name, notes=notes, course_id=course_id)
    return redirect("/")


@lti_role_required(ADMINS)
@page
def submit_edit_track(request):
    course_id = get_lti_param(request, "custom_canvas_course_id")
    name = post_param(request, "name")
    notes = post_param(request, "notes")
    track_id = post_param(request, "id")
    result_list = Track.objects.filter(pk=track_id, course_id=course_id)
    if len(result_list) == 1:
        result_list[0].update(name=name, notes=notes)
    elif len(result_list) > 1:
        raise MULTIPLE_OBJECTS
    else:
        raise MISSING_TRACK
    return redirect("/")


@lti_role_required(ADMINS)
@page
def delete_track(request, track_id):
    """
    NOTE: When a track gets deleted, stages on the track do not get deleted.
    Decide whether or not this should be the case.
    """
    course_id = get_lti_param(request, "custom_canvas_course_id")
    t = Track.objects.filter(pk=track_id, course_id=course_id)
    if len(t) == 1:
        t[0].delete()
        stage_urls = StageUrl.objects.filter(track__pk=track_id)
        for url in stage_urls:
            url.delete()
    elif len(t) > 1:
        raise MULTIPLE_OBJECTS
    else:
        raise MISSING_TRACK
    return redirect("/")
