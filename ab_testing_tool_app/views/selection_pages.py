from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.utils.http import urlencode
from django_auth_lti.decorators import lti_role_required

from ab_testing_tool_app.models import Track, InterventionPointUrl, InterventionPoint
from ab_testing_tool_app.controllers import (get_uninstalled_stages, stage_url,
    post_param)
from ab_testing_tool_app.constants import STAGE_URL_TAG, ADMINS
from ab_testing_tool_app.canvas import get_lti_param
from ab_testing_tool_app.exceptions import (MISSING_RETURN_TYPES_PARAM,
    MISSING_RETURN_URL)


@lti_role_required(ADMINS)
def resource_selection(request):
    """ docs: https://canvas.instructure.com/doc/api/file.link_selection_tools.html """
    course_id = get_lti_param(request, "custom_canvas_course_id")
    ext_content_return_types = request.POST.getlist('ext_content_return_types')
    if ext_content_return_types != ['lti_launch_url']:
        raise MISSING_RETURN_TYPES_PARAM
    content_return_url = request.POST.get('ext_content_return_url')
    if not content_return_url:
        raise MISSING_RETURN_URL
    context = {"content_return_url": content_return_url,
               "stages": get_uninstalled_stages(request),
               "tracks": Track.objects.filter(course_id=course_id),
               }
    return render_to_response("add_module_item.html", context)


@lti_role_required(ADMINS)
def submit_selection(request):
    stage_id = post_param(request, "stage_id")
    stage = get_object_or_404(InterventionPoint, pk=stage_id)
    page_url = stage_url(request, stage_id)
    page_name = stage.name
    content_return_url = post_param(request, "content_return_url")
    params = {"return_type": "lti_launch_url",
               "url": page_url,
               #"title": "Title",
               "text": page_name}
    return redirect("%s?%s" % (content_return_url, urlencode(params)))


@lti_role_required(ADMINS)
def submit_selection_new_stage(request):
    course_id = get_lti_param(request, "custom_canvas_course_id")
    name = post_param(request, "name")
    notes = post_param(request, "notes")
    stage = InterventionPoint.objects.create(name=name, notes=notes, course_id=course_id)
    stageurls = [(k,v) for (k,v) in request.POST.iteritems() if STAGE_URL_TAG in k and v]
    for (k,v) in stageurls:
        _, track_id = k.split(STAGE_URL_TAG)
        InterventionPointUrl.objects.create(url=v, stage_id=stage.id, track_id=track_id)
    page_url = stage_url(request, stage.id)
    page_name = stage.name
    content_return_url = request.REQUEST.get("content_return_url")
    params = {"return_type": "lti_launch_url",
               "url": page_url,
               #"title": "Title",
               "text": page_name}
    return redirect("%s?%s" % (content_return_url, urlencode(params)))

