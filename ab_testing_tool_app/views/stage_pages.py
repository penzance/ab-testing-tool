from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.core.urlresolvers import reverse
from django_auth_lti.decorators import lti_role_required
from random import choice

from ab_testing_tool_app.constants import ADMINS, STAGE_URL_TAG
from ab_testing_tool_app.models import (Stage, Track, StageUrl, CourseSettings,
    CourseStudent)
from ab_testing_tool_app.canvas import get_lti_param
from ab_testing_tool_app.controllers import (stage_is_installed, format_url,
    post_param)
from ab_testing_tool_app.exceptions import (UNAUTHORIZED_ACCESS,
    DELETING_INSTALLED_STAGE, COURSE_TRACKS_NOT_FINALIZED,
    NO_URL_FOR_TRACK, NO_TRACKS_FOR_COURSE)


def deploy_stage(request, stage_id):
    """Delivers randomly one of the urls in stage if user is not an admin, or
       edit_stage panel if admin.
       Note: Do not put @lti_role_required(ADMINS) here, as students can reach
       this page.
       TODO: Have admin able to preview stages as a student would see them
       """
    course_id = get_lti_param(request, "custom_canvas_course_id")
    # TODO: replace the following code with verification.is_allowed
    # when that code makes it into django_auth_lti master
    user_roles = get_lti_param(request, "roles")
    
    # If user is an admin, let them edit the stage
    if set(ADMINS) & set(user_roles):
        return redirect(reverse("modules_page_edit_stage", args=(stage_id,)))
    
    # Otherwise, user is a student.  Tracks for the course must be finalized
    # for a student to be able to access content from the ab_testing_tool
    if not CourseSettings.get_is_finalized(course_id):
        raise COURSE_TRACKS_NOT_FINALIZED
    
    student_id = get_lti_param(request, "custom_canvas_user_login_id")
    
    # Get or create an object to track the student for this course
    try:
        student = CourseStudent.objects.get(student_id=student_id, course_id=course_id)
    except CourseStudent.DoesNotExist:
        # If this is a new student or the student doesn't yet have a track,
        # assign the student to a track
        # TODO: expand this code to allow multiple randomization procedures
        tracks = Track.objects.filter(course_id=course_id)
        if not tracks:
            raise NO_TRACKS_FOR_COURSE
        chosen_track = choice(tracks)
        student = CourseStudent.objects.create(
                student_id=student_id, course_id=course_id, track=chosen_track)
    
    # Retrieve the url for the student's track at the current intervention point
    # Return an error page if there is no url configured.
    try:
        chosen_stage_url = StageUrl.objects.get(stage__pk=stage_id, track=student.track)
    except StageUrl.DoesNotExist:
        raise NO_URL_FOR_TRACK
    if not chosen_stage_url.url:
        raise NO_URL_FOR_TRACK
    return redirect(chosen_stage_url.url)


@lti_role_required(ADMINS)
def create_stage(request):
    """ Note: Canvas fetches all pages within iframe with POST request,
        requiring separate template render function. This also breaks CSRF
        token validation if CSRF Middleware is turned off. """
    course_id = get_lti_param(request, "custom_canvas_course_id")
    #Note: Refer to template. (t,None) is passed as there are no existing StageUrls for a new stage
    context = {"tracks" : [(t, None) for t in
                           Track.objects.filter(course_id=course_id)],
               "cancel_url": "/#tabs-2"}
    return render_to_response("edit_stage.html", context)


@lti_role_required(ADMINS)
def submit_create_stage(request):
    """ Note: request will always be POST because Canvas fetches pages within iframe by POST
        TODO: use Django forms library to save instead of getting individual POST params """
    course_id = get_lti_param(request, "custom_canvas_course_id")
    name = post_param(request, "name")
    notes = post_param(request, "notes")
    t = Stage.objects.create(name=name, notes=notes, course_id=course_id)
    stageurls = [(k,v) for (k,v) in request.POST.iteritems() if STAGE_URL_TAG in k and v]
    for (k,v) in stageurls:
        _,track_id = k.split(STAGE_URL_TAG)
        StageUrl.objects.create(url=format_url(v), stage_id=t.id, track_id=track_id)
    return redirect("/#tabs-2")


@lti_role_required(ADMINS)
def modules_page_edit_stage(request, stage_id):
    context = edit_stage_common(request, stage_id)
    context["cancel_url"] = get_lti_param(request, "launch_presentation_return_url") + "/modules"
    return render_to_response("modules_page_edit_stage.html", context)

@lti_role_required(ADMINS)
def edit_stage(request, stage_id):
    context = edit_stage_common(request, stage_id)
    context["cancel_url"] = "/#tabs-2"
    return render_to_response("edit_stage.html", context)

def edit_stage_common(request, stage_id):
    """ Common core shared bewteen edit_stage and modules_page_edit_stage """
    stage = get_object_or_404(Stage, pk=stage_id)
    course_id = get_lti_param(request, "custom_canvas_course_id")
    if course_id != stage.course_id:
        raise UNAUTHORIZED_ACCESS
    all_tracks = Track.objects.filter(course_id=course_id)
    track_urls = []
    for track in all_tracks:
        # This is a search for the joint unique index of StageUrl, so it
        # should not ever return multiple objects
        try:
            stage_url = StageUrl.objects.get(stage__pk=stage_id, track=track)
            track_urls.append((track, stage_url))
        except StageUrl.DoesNotExist:
            track_urls.append((track, None))
    context = {"stage": stage,
               "tracks": track_urls,
               "is_installed": stage_is_installed(request, stage),
               #TODO: "installed_module": installed_module,
               }
    return context


@lti_role_required(ADMINS)
def submit_edit_stage(request, stage_id):
    """ Note: Only allowed if admin has privileges on the particular course.
        TODO: consider using Django forms to save rather of getting individual POST params """
    stage = get_object_or_404(Stage, pk=stage_id)
    course_id = get_lti_param(request, "custom_canvas_course_id")
    name = post_param(request, "name")
    notes = post_param(request, "notes")
    if course_id != stage.course_id:
        raise UNAUTHORIZED_ACCESS
    stage.update(name=name, notes=notes)
    # StageUrl creation
    stageurls = [(k,v) for (k,v) in request.POST.iteritems() if STAGE_URL_TAG in k and v]
    for (k,v) in stageurls:
        _, track_id = k.split(STAGE_URL_TAG)
        # This is a search for the joint unique index of StageUrl, so it
        # should not ever return multiple objects
        try:
            stage_url = StageUrl.objects.get(stage__pk=stage_id, track__pk=track_id)
            stage_url.update(url=format_url(v))
        except StageUrl.DoesNotExist:
            StageUrl.objects.create(url=v, stage_id=stage_id, track_id=track_id)
    return redirect("/#tabs-2")


@lti_role_required(ADMINS)
def delete_stage(request, stage_id):
    """ Note: Installed stages are not allowed to be deleted
        Note: attached StageUrls are deleted via cascading delete """
    stage = get_object_or_404(Stage, pk=stage_id)
    course_id = get_lti_param(request, "custom_canvas_course_id")
    if course_id != stage.course_id:
        raise UNAUTHORIZED_ACCESS
    if stage_is_installed(request, stage):
        raise DELETING_INSTALLED_STAGE
    stage.delete()
    return redirect("/#tabs-2")
