import json
from canvas_sdk import RequestContext
from canvas_sdk.methods.modules import list_module_items, list_modules

from ab_testing_tool.models import Treatment
#TODO: change from secure.py setting to oauth handoff
from ab_testing_tool.settings.secure import COURSE_OAUTH_TOKEN


class InvalidResponseError(Exception):
    """ TODO: Move this to canvas_sdk_python """
    pass


def get_lti_param(request, key):
    """ TODO: Add this function to Django auth lti library """
    return request.session["LTI_LAUNCH"][key]


def get_canvas_request_context(request):
    oauth_token = COURSE_OAUTH_TOKEN
    canvas_url = "https://{0}/api".format(get_lti_param(request, "custom_canvas_api_domain"))
    return RequestContext(oauth_token, canvas_url)


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


def treatment_url(request, t_id):
    return "%s/treatment/%s" % (get_full_host(request), t_id)


def get_uninstalled_treatments(request):
    course_id = get_lti_param(request, "custom_canvas_course_id")
    request_context =  get_canvas_request_context(request)
    response = list_modules(request_context, course_id, "content_details")
    all_modules = parse_response(response)
    installed_treatment_urls = []
    for module in all_modules:
        response = list_module_items(request_context, course_id,
                                     module["id"], "content_details")
        treatment_urls = [t["external_url"] for t in parse_response(response)
                          if t["type"] == "ExternalTool"]
        installed_treatment_urls.extend(treatment_urls)
    treatments = [t for t in Treatment.objects.all()
                  if treatment_url(request, t.id) not in installed_treatment_urls]
    return treatments
