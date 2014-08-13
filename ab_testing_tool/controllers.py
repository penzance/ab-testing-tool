import json
from ab_testing_tool.models import Stage
from canvas import get_canvas_request_context, list_module_items, list_modules

class InvalidResponseError(Exception):
    """ TODO: Move this to canvas_sdk_python """
    pass

def get_lti_param(request, key):
    """ TODO: Add this function to Django auth lti library """
    return request.session["LTI_LAUNCH"][key]

def parse_response(sdk_response):
    """ TODO: Move this function to canvas_sdk_python so that all sdk
        functions return python objects instead of response objects """
    if sdk_response.ok:
        return json.loads(sdk_response.text)
    else:
        raise InvalidResponseError

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
    response = list_modules(request_context, course_id, "content_details")
    all_modules = parse_response(response)
    installed_stage_urls = []
    for module in all_modules:
        response = list_module_items(request_context, course_id,
                                     module["id"], "content_details")
        stage_urls = [t["external_url"] for t in parse_response(response)
                          if t["type"] == "ExternalTool"]
        installed_stage_urls.extend(stage_urls)
    stages = [t for t in Stage.objects.all()
                  if stage_url(request, t.id) not in installed_stage_urls]
    return stages
