from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.utils.http import urlencode
from django_auth_lti.decorators import lti_role_required

from ab_tool.models import Track, InterventionPointUrl, InterventionPoint
from ab_tool.controllers import (get_uninstalled_intervention_points, intervention_point_url,
    post_param)
from ab_tool.constants import STAGE_URL_TAG, ADMINS
from ab_tool.canvas import get_lti_param
from ab_tool.exceptions import (MISSING_RETURN_TYPES_PARAM,
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
               "intervention_points": get_uninstalled_intervention_points(request),
               "tracks": Track.objects.filter(course_id=course_id),
               }
    return render_to_response("ab_tool/add_module_item.html", context)


@lti_role_required(ADMINS)
def submit_selection(request):
    intervention_point_id = post_param(request, "intervention_point_id")
    intervention_point = get_object_or_404(InterventionPoint, pk=intervention_point_id)
    page_url = intervention_point_url(request, intervention_point_id)
    page_name = intervention_point.name
    content_return_url = post_param(request, "content_return_url")
    params = {"return_type": "lti_launch_url",
               "url": page_url,
               #"title": "Title",
               "text": page_name}
    return redirect("%s?%s" % (content_return_url, urlencode(params)))


@lti_role_required(ADMINS)
def submit_selection_new_intervention_point(request):
    course_id = get_lti_param(request, "custom_canvas_course_id")
    name = post_param(request, "name")
    notes = post_param(request, "notes")
    intervention_point = InterventionPoint.objects.create(name=name, notes=notes, course_id=course_id)
    intervention_pointurls = [(k,v) for (k,v) in request.POST.iteritems() if STAGE_URL_TAG in k and v]
    for (k,v) in intervention_pointurls:
        _, track_id = k.split(STAGE_URL_TAG)
        InterventionPointUrl.objects.create(url=v, intervention_point_id=intervention_point.id, track_id=track_id)
    page_url = intervention_point_url(request, intervention_point.id)
    page_name = intervention_point.name
    content_return_url = request.REQUEST.get("content_return_url")
    params = {"return_type": "lti_launch_url",
               "url": page_url,
               #"title": "Title",
               "text": page_name}
    return redirect("%s?%s" % (content_return_url, urlencode(params)))

