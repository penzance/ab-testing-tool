from django.shortcuts import render_to_response, redirect
from django.core.urlresolvers import reverse
from django_auth_lti.decorators import lti_role_required
from random import choice

from ab_testing_tool.pages.main_pages import ADMINS, STAGE_URL_TAG
from ab_testing_tool.models import Stage, Track, StageUrl
from ab_testing_tool.canvas import (list_module_items, list_modules, create_module_item,
                                    get_lti_param)
from ab_testing_tool.controllers import get_canvas_request_context, stage_url
from ab_testing_tool.decorators import page

@page
def deploy_stage(request, t_id):
    """
    Note: Do not put @lti_role_required(ADMINS) here. @lti_role_required(const.STUDENT)
    Description: Delivers randomly one of the two urls in stage.
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
    """
    Note: Canvas fetches all pages within iframe with POST request,
    requiring separate template render function.
    This also breaks CSRF token validation if CSRF Middleware is turned off.
    """
    context = {"tracks" : [(t,None) for t in Track.objects.all()]}
    return render_to_response("edit_stage.html", context)


@lti_role_required(ADMINS)
@page
def submit_create_stage(request):
    """
    Note: request will always be POST because Canvas fetches pages within iframe by POST
    TODO: use Django forms library to save instead of getting individual POST params
    """
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
def submit_edit_stage(request):
    """
    Update stage only allowed if admin has privileges on the particular course.
    TODO: use Django forms library to save instead of getting individual POST params
    """
    course_id = get_lti_param(request, "custom_canvas_course_id")
    name = request.POST["name"]
    notes = request.POST["notes"]
    t_id = request.POST["id"]
    result_list = Stage.objects.filter(pk=t_id, course_id=course_id)
    if len(result_list) == 1:
        result_list[0].update(name=name, notes=notes)
    elif len(result_list) > 1:
        raise Exception("Multiple objects returned.")
    else:
        raise Exception("No stage with ID '{0}' found".format(t_id))
    #StageUrl creation
    stageurls = [(k,v) for (k,v) in request.POST.iteritems() if STAGE_URL_TAG in k and v]
    for (k,v) in stageurls:
        _,track_id = k.split(STAGE_URL_TAG)
        stage_result_list = StageUrl.objects.filter(stage__pk=t_id, track__pk=track_id)
        if len(stage_result_list) == 1:
            stage_result_list[0].update(url=v)
        elif len(result_list) > 1:
            raise Exception("Multiple objects returned.")
        else:
            StageUrl.objects.create(url=v, stage_id=t_id, track_id=track_id)
    return redirect("/#tabs-2")

@lti_role_required(ADMINS)
@page
def edit_stage(request, t_id):
    all_tracks = Track.objects.all()
    track_urls = []
    for t in all_tracks:
        stage_url = StageUrl.objects.filter(stage__pk=t_id, track=t)
        if stage_url:
            track_urls.append((t, stage_url[0]))
        else:
            track_urls.append((t, None))
    context = {"stage": Stage.objects.get(pk=t_id),
               "tracks": track_urls,
               }
    return render_to_response("edit_stage.html", context)

@lti_role_required(ADMINS)
def delete_stage(request, t_id):
    """
    TODO: !!! Make call to canvas API to remove stage as module item from
    any modules it is installed. May need to add module_item_id as DB attribute.
    """
    course_id = get_lti_param(request, "custom_canvas_course_id")
    t = Stage.objects.filter(pk=t_id, course_id=course_id)
    if len(t) == 1:
        t[0].delete()
        stage_urls = StageUrl.objects.filter(stage__pk=t_id)
        for url in stage_urls:
            url.delete()
    elif len(t) > 1:
        raise Exception("Multiple objects returned.")
    else:
        raise Exception("No stage with ID '{0}' found".format(t_id))
    return redirect("/#tabs-2")

@lti_role_required(ADMINS)
@page
def add_stage_to_module(request, t_id):
    """
    TODO: Finish this to be able to add stage to a module from control panel
    """
    course_id = get_lti_param(request, "custom_canvas_course_id")
    request_context =  get_canvas_request_context(request)
    modules = list_modules(request_context, course_id, "content_details")
    module_id = modules[0]["id"]
    item_results = list_module_items(request_context, course_id, module_id)
    # canvas_sdk.methods.modules.create_module_item(
    #        request_ctx, course_id, module_id, module_item_type,
    #        module_item_content_id, module_item_page_url,
    #        module_item_external_url,
    #        module_item_completion_requirement_min_score)
    create_module_item(request_context, course_id, module_id, stage_url(request, t_id))
    return redirect("/")
