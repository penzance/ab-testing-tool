from ab_testing_tool.settings.secure import COURSE_OAUTH_TOKEN #Needed token to interact with Canvas, #CHANGEME to developer token
from canvas_sdk import RequestContext
import json


def _get_lti_param(request, key):
    """TODO: Add this function to Django auth lti library"""
    return request.session["LTI_LAUNCH"][key]

def _establish_canvas_sdk(request):
    oauth_token = COURSE_OAUTH_TOKEN
    canvas_url = "https://{0}/api".format(_get_lti_param(request, "custom_canvas_api_domain"))
    return RequestContext(oauth_token, canvas_url)

class InvalidResponseError(Exception):
    """TODO: Move this to canvas_sdk_python"""
    pass

def parse_response(sdk_response):
    """TODO: Move this function to canvas_sdk_python so that all sdk functions return python objects instead of response objects"""
    if sdk_response.ok:
        return json.loads(sdk_response.text)
    else:
        raise InvalidResponseError

