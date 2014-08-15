from django.shortcuts import render_to_response, redirect
from django_auth_lti.decorators import lti_role_required

from ab_testing_tool.pages.main_pages import ADMINS
from ab_testing_tool.models import Track, StageUrl
from ab_testing_tool.canvas import get_lti_param
from ab_testing_tool.decorators import page


@lti_role_required(ADMINS)
@page
def create_track(request):
    return render_to_response("edit_track.html")


@lti_role_required(ADMINS)
@page
def edit_track(request, track_id):
    context = {"track": Track.objects.get(pk=track_id)}
    return render_to_response("edit_track.html", context)


@lti_role_required(ADMINS)
@page
def submit_create_track(request):
    course_id = get_lti_param(request, "custom_canvas_course_id")
    name = request.POST["name"]
    notes = request.POST["notes"]
    Track.objects.create(name=name, notes=notes, course_id=course_id)
    return redirect("/")


@lti_role_required(ADMINS)
@page
def submit_edit_track(request):
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
        raise Exception("Multiple objects returned.")
    else:
        raise Exception("No track with ID '{0}' found".format(track_id))
    return redirect("/")
