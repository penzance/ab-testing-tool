import json
import canvas_sdk.methods.modules
from canvas_sdk import RequestContext

#TODO: change from secure.py setting to oauth handoff
from ab_testing_tool.settings.secure import COURSE_OAUTH_TOKEN
from ab_testing_tool_app.exceptions import (MISSING_LTI_PARAM, MISSING_LTI_LAUNCH,
    INVALID_SDK_RESPONSE, NO_SDK_RESPONSE)


"""
Canvas API related methods are located in this module
"""

def list_module_items(request_context, course_id, module_id):
    try:
        return canvas_sdk.methods.modules.list_module_items(
                    request_context, course_id, module_id, "content_details").json()
    except:
        raise NO_SDK_RESPONSE

def list_modules(request_context, course_id):
    try:
        return canvas_sdk.methods.modules.list_modules(request_context,
                    course_id, "content_details").json()
    except:
        raise NO_SDK_RESPONSE

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
