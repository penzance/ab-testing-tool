import json
from ab_testing_tool.models import Stage
from canvas import (get_canvas_request_context, list_module_items, list_modules,
                    get_lti_param)


def get_full_host(request):
    if request.is_secure():
        return "https://" + request.get_host()
    else:
        return "http://" + request.get_host()

def stage_url(request, t_id):
    return "%s/stage/%s" % (get_full_host(request), t_id)

def get_uninstalled_stages(request):
    course_id = get_lti_param(request, "custom_canvas_course_id")
    request_context =  get_canvas_request_context(request)
    all_modules = list_modules(request_context, course_id)
    installed_stage_urls = []
    for module in all_modules:
        module_items = list_module_items(request_context, course_id, module["id"])
        stage_urls = [t["external_url"] for t in module_items
                          if t["type"] == "ExternalTool"]
        installed_stage_urls.extend(stage_urls)
    stages = [t for t in Stage.objects.all()
                  if stage_url(request, t.id) not in installed_stage_urls]
    return stages
