from django.shortcuts import render_to_response, redirect
from django.core.urlresolvers import reverse
from django_auth_lti.decorators import lti_role_required
from random import choice

from ab_testing_tool.constants import ADMINS, STAGE_URL_TAG
from ab_testing_tool.models import Stage, Track, StageUrl
from ab_testing_tool.canvas import get_lti_param
from ab_testing_tool.controllers import stage_is_installed
from ab_testing_tool.decorators import page
from ab_testing_tool.exceptions import (MULTIPLE_OBJECTS, MISSING_STAGE,
    DELETING_INSTALLED_STAGE, UNAUTHORIZED_ACCESS)


@page
def deploy_stage(request, t_id):
    """Delivers randomly one of the urls in stage if user is not an admin, or
       edit_stage panel if admin.
       Note: Do not put @lti_role_required(ADMINS) here, as students can reach
       this page.
       TODO: Extend this by delivering stage as determined by track student is on
       TODO: Have admin able to preview stages as a student would see them
       
       """
    # TODO: replace the following three lines with verification.is_allowed
    # when that code makes it into django_auth_lti master
    lti_launch = request.session.get('LTI_LAUNCH', None)
    user_roles = lti_launch.get('roles', [])
    if set(ADMINS) & set(user_roles):
        return redirect(reverse("edit_stage", args=(t_id,)))
    stage_urls = StageUrl.objects.filter(stage__pk=t_id)
    stage_urls = stage_urls.exclude(url__isnull=True).exclude(url__exact='')
    chosen_url = choice(stage_urls)
    return redirect(chosen_url.url)


@lti_role_required(ADMINS)
@page
def create_stage(request):
    """ Note: Canvas fetches all pages within iframe with POST request, requiring separate
        template render function. This also breaks CSRF token validation if CSRF Middleware is turned off. """
    course_id = get_lti_param(request, "custom_canvas_course_id")
    context = {"tracks" : [(t, None) for t in
                           Track.objects.filter(course_id=course_id)]}
    return render_to_response("edit_stage.html", context)


@lti_role_required(ADMINS)
@page
def submit_create_stage(request):
    """ Note: request will always be POST because Canvas fetches pages within iframe by POST
        TODO: use Django forms library to save instead of getting individual POST params """
    course_id = get_lti_param(request, "custom_canvas_course_id")
    name = request.POST["name"]
    notes = request.POST["notes"]
    t = Stage.objects.create(name=name, notes=notes, course_id=course_id)
    stageurls = [(k,v) for (k,v) in request.POST.iteritems() if STAGE_URL_TAG in k and v]
    for (k,v) in stageurls:
        _,track_id = k.split(STAGE_URL_TAG)
        StageUrl.objects.create(url=v, stage_id=t.id, track_id=track_id)
    return redirect("/#tabs-2")


@lti_role_required(ADMINS)
@page
def edit_stage(request, t_id):
    course_id = get_lti_param(request, "custom_canvas_course_id")
    stage = Stage.objects.get(pk=t_id)
    if course_id != stage.course_id:
        raise UNAUTHORIZED_ACCESS
    all_tracks = Track.objects.filter(course_id=course_id)
    track_urls = []
    for t in all_tracks:
        url = StageUrl.objects.filter(stage__pk=t_id, track=t)
        if url and len(url) == 1:
            track_urls.append((t, url[0]))
        elif len(url) > 1:
            raise MULTIPLE_OBJECTS
        else:
            track_urls.append((t, None))
    context = {"stage": stage,
               "tracks": track_urls,
               "is_installed": stage_is_installed(request, stage),
               #TODO: "installed_module": installed_module,
               }
    return render_to_response("edit_stage.html", context)


@lti_role_required(ADMINS)
@page
def submit_edit_stage(request):
    """Note:Only allowed if admin has privileges on the particular course.
       TODO: consider using Django forms to save rather of getting individual POST params"""
    course_id = get_lti_param(request, "custom_canvas_course_id")
    name = request.POST["name"]
    notes = request.POST["notes"]
    t_id = request.POST["id"]
    result_list = Stage.objects.filter(pk=t_id, course_id=course_id)
    if len(result_list) == 1:
        result_list[0].update(name=name, notes=notes)
    elif len(result_list) > 1:
        raise MULTIPLE_OBJECTS
    else:
        raise MISSING_STAGE
    #StageUrl creation
    stageurls = [(k,v) for (k,v) in request.POST.iteritems() if STAGE_URL_TAG in k and v]
    for (k,v) in stageurls:
        _,track_id = k.split(STAGE_URL_TAG)
        stage_result_list = StageUrl.objects.filter(stage__pk=t_id, track__pk=track_id)
        if len(stage_result_list) == 1:
            stage_result_list[0].update(url=v)
        elif len(result_list) > 1:
            raise MULTIPLE_OBJECTS
        else:
            StageUrl.objects.create(url=v, stage_id=t_id, track_id=track_id)
    return redirect("/#tabs-2")


@lti_role_required(ADMINS)
@page
def delete_stage(request, t_id):
    """Note: Installed stages are not allowed to be deleted"""
    course_id = get_lti_param(request, "custom_canvas_course_id")
    t = Stage.objects.filter(pk=t_id, course_id=course_id)
    if len(t) == 1:
        stage = t[0]
        if stage_is_installed(request, stage):
            raise DELETING_INSTALLED_STAGE
        stage.delete()
        stage_urls = StageUrl.objects.filter(stage__pk=t_id)
        for url in stage_urls:
            url.delete()
    elif len(t) > 1:
        raise MULTIPLE_OBJECTS
    else:
        raise MISSING_STAGE
    return redirect("/#tabs-2")
