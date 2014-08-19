import json
import canvas_sdk
from canvas_sdk import RequestContext

#TODO: change from secure.py setting to oauth handoff
from ab_testing_tool.settings.secure import COURSE_OAUTH_TOKEN
from ab_testing_tool.exceptions import MISSING_LTI_PARAM, MISSING_LTI_LAUNCH,\
    INVALID_SDK_RESPONSE, NO_SDK_RESPONSE


"""
Canvas API related methods are located in this module
"""

def list_module_items(request_context, course_id, module_id):
    return parse_response(canvas_sdk.methods.modules.list_module_items(
                    request_context, course_id, module_id, "content_details"))

def list_modules(request_context, course_id):
    return parse_response(canvas_sdk.methods.modules.list_modules(
                    request_context, course_id, "content_details"))


def create_module_item(request_context, course_id, module_id, stage_url):
    #TODO: unused, untested
    return parse_response(canvas_sdk.methods.modules.create_module_item(
                    request_context, course_id, module_id, "ExternalTool",
                    "ab_testing_tool", "1", stage_url, None ))

def parse_response(sdk_response):
    """ TODO: Move this function to canvas_sdk_python so that all sdk
        functions return python objects instead of response objects """
    if not sdk_response.ok:
        raise NO_SDK_RESPONSE
    try:
        return json.loads(sdk_response.text)
    except ValueError:
        raise INVALID_SDK_RESPONSE


def get_lti_param(request, key):
    """
    Note: Not Canvas related, but located here to avoid cyclic imports
    TODO: Add this function to Django auth lti library
    """
    if "LTI_LAUNCH" not in request.session:
        raise MISSING_LTI_LAUNCH
    if key not in request.session["LTI_LAUNCH"]:
        raise MISSING_LTI_PARAM
    return request.session["LTI_LAUNCH"][key]

def get_canvas_request_context(request):
    oauth_token = COURSE_OAUTH_TOKEN
    canvas_domain = get_lti_param(request, "custom_canvas_api_domain")
    canvas_url = "https://{0}/api".format(canvas_domain)
    return RequestContext(oauth_token, canvas_url)


def get_module_items(all_modules, request_context, course_id):
    """
    Takes all_modules dict and fetches module items for each module to be added
    to the returned dict.
    """
    for module in all_modules:
        module["module_items"] = list_module_items(request_context, course_id, module["id"])
    return all_modules
