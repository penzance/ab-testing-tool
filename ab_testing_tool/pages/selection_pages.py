from django.shortcuts import render_to_response, redirect
from django.core.urlresolvers import reverse
from ab_testing_tool.models import Track, StageUrl, Stage
from ab_testing_tool.controllers import get_uninstalled_stages, stage_url
from django.http.response import HttpResponse
from django.utils.http import urlencode
from ab_testing_tool.pages.main_pages import STAGE_URL_TAG
from ab_testing_tool.canvas import get_lti_param



def resource_selection(request):
    """ docs: https://canvas.instructure.com/doc/api/file.link_selection_tools.html """
    ext_content_return_types = request.REQUEST.get('ext_content_return_types')
    if ext_content_return_types == [u'lti_launch_url']:
        return HttpResponse("Error: invalid ext_content_return_types: %s" %
                            ext_content_return_types)
    content_return_url = request.REQUEST.get('ext_content_return_url')
    if not content_return_url:
        return HttpResponse("Error: no ext_content_return_url")

    context = {"content_return_url": content_return_url,
               "stages": get_uninstalled_stages(request),
               "tracks": [(t,None) for t in Track.objects.all()],
               }
    return render_to_response("add_module_item.html", context)


def submit_selection(request):
    stage_id = request.REQUEST.get("stage_id")
    t = Stage.objects.get(pk=stage_id)
    page_url = stage_url(request, stage_id)
    print stage_id, page_url
    page_name = t.name # TODO: replace with value from DB
    content_return_url = request.REQUEST.get("content_return_url")
    params = {"return_type": "lti_launch_url",
               "url": page_url,
               #"title": "Title",
               "text": page_name}
    return redirect("%s?%s" % (content_return_url, urlencode(params)))


def submit_selection_new_stage(request):
    course_id = get_lti_param(request, "custom_canvas_course_id")
    name = request.POST["name"]
    notes = request.POST["notes"]
    t = Stage.objects.create(name=name, notes=notes, course_id=course_id)
    stageurls = [(k,v) for (k,v) in request.POST.iteritems() if STAGE_URL_TAG in k and v]
    for (k,v) in stageurls:
        _,track_id = k.split(STAGE_URL_TAG)
        StageUrl.objects.create(url=v, stage_id=t.id, track_id=track_id)
    page_url = stage_url(request, t.id)
    page_name = t.name # TODO: replace with value from DB
    content_return_url = request.REQUEST.get("content_return_url")
    params = {"return_type": "lti_launch_url",
               "url": page_url,
               #"title": "Title",
               "text": page_name}
    return redirect("%s?%s" % (content_return_url, urlencode(params)))

